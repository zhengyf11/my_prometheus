import base64
import json
import logging
import os
import time
import urllib.error
import urllib.request

from .command import command_exists, run
from .files import backup_file, copy_file, ensure_dir, write_managed_file
from .packages import install_grafana_package
from .state import read_grafana_credentials, read_state, write_grafana_credentials
from .systemd import enable_now, restart


LOG = logging.getLogger(__name__)


def install_grafana(ctx):
    LOG.info("installing Grafana %s", ctx.grafana_version)
    was_installed = install_grafana_package(ctx)
    previous_state = read_state(ctx)
    ctx.grafana_preexisting = previous_state.get("grafana_preexisting", was_installed)
    ensure_dir(ctx, ctx.grafana_provisioning_dir / "datasources")
    ensure_dir(ctx, ctx.grafana_provisioning_dir / "dashboards")
    ensure_dir(ctx, ctx.grafana_dashboard_dir, owner="grafana", group="grafana")
    configure_grafana_ini(ctx)
    provision_datasource(ctx)
    provision_dashboards(ctx)
    enable_now(ctx, "grafana-server")
    restart(ctx, "grafana-server")
    wait_for_grafana(ctx)
    prepare_grafana_password(ctx, was_installed)


def prepare_grafana_password(ctx, was_installed):
    if ctx.reset_grafana_admin_password or not was_installed:
        ctx.ensure_grafana_admin_password()
        set_admin_password(ctx)
        ctx.grafana_password_changed = True
        if ctx.generated_grafana_password:
            write_grafana_credentials(ctx)
        return

    if not ctx.grafana_admin_password:
        credentials = read_grafana_credentials(ctx)
        if credentials.get("password"):
            ctx.grafana_admin_password = credentials["password"]
            LOG.info("using stored Grafana credentials for health checks")
    LOG.info("Grafana admin password unchanged; use --reset-grafana-admin-password to reset it")


def configure_grafana_ini(ctx):
    path = "/etc/grafana/grafana.ini"
    values = {
        "server": {
            "http_addr": grafana_http_addr(ctx.grafana_listen_address),
            "http_port": str(ctx.grafana_port),
        },
        "users": {
            "allow_sign_up": "false",
        },
    }
    update_ini_values(ctx, path, values)


def update_ini_values(ctx, path, values):
    if ctx.dry_run:
        LOG.info("[dry-run] update %s", path)
        return
    stat_result = os.stat(path)
    with open(path, "r") as handle:
        lines = handle.readlines()

    output = []
    current = None
    seen = {}
    for section in values:
        seen[section] = set()

    def emit_missing(section):
        if section not in values:
            return
        for key, value in values[section].items():
            if key not in seen[section]:
                output.append("{0} = {1}\n".format(key, value))
                seen[section].add(key)

    changed = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            emit_missing(current)
            current = stripped[1:-1].strip()
            output.append(line)
            continue

        if current in values:
            candidate = stripped[1:].strip() if stripped.startswith(";") else stripped
            if "=" in candidate:
                key = candidate.split("=", 1)[0].strip()
                if key in values[current]:
                    if not stripped.startswith(";"):
                        old_value = candidate.split("=", 1)[1].strip()
                        new_value = values[current][key]
                        if old_value != new_value and not ctx.force:
                            raise RuntimeError(
                                "{0} [{1}] {2} is already set to {3}; rerun with --force to change it to {4}".format(
                                    path, current, key, old_value, new_value
                                )
                            )
                    new_line = "{0} = {1}\n".format(key, values[current][key])
                    output.append(new_line)
                    seen[current].add(key)
                    if line != new_line:
                        changed = True
                    continue
        output.append(line)

    emit_missing(current)
    for section in values:
        if seen[section] == set(values[section].keys()):
            continue
        output.append("\n[{0}]\n".format(section))
        for key, value in values[section].items():
            if key not in seen[section]:
                output.append("{0} = {1}\n".format(key, value))
                seen[section].add(key)
                changed = True

    content = "".join(output)
    old_content = "".join(lines)
    if content == old_content and not changed:
        return
    backup = backup_file(path)
    LOG.info("backed up %s to %s", path, backup)
    with open(path, "w") as handle:
        handle.write(content)
    os.chmod(path, stat_result.st_mode & 0o777)
    os.chown(path, stat_result.st_uid, stat_result.st_gid)


def grafana_http_addr(address):
    if address in (None, "", "0.0.0.0", "::", "[::]"):
        return ""
    return str(address)


def provision_datasource(ctx):
    content = """apiVersion: 1

datasources:
  - name: Prometheus
    uid: Prometheus
    type: prometheus
    access: proxy
    url: {prometheus_url}
    isDefault: true
    editable: true
""".format(prometheus_url=ctx.prometheus_url)
    write_managed_file(
        ctx,
        ctx.grafana_provisioning_dir / "datasources" / "prometheus.yml",
        content,
        mode=0o640,
        owner="root",
        group="grafana",
    )


def provision_dashboards(ctx):
    provider = """apiVersion: 1

providers:
  - name: my-prometheus
    orgId: 1
    folder: Linux Hosts
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
"""
    write_managed_file(
        ctx,
        ctx.grafana_provisioning_dir / "dashboards" / "dashboards.yml",
        provider,
        mode=0o640,
        owner="root",
        group="grafana",
    )
    copy_file(
        ctx,
        ctx.grafana_assets_dir / "dashboards" / "node-overview.json",
        ctx.grafana_dashboard_dir / "node-overview.json",
        mode=0o644,
        owner="grafana",
        group="grafana",
    )
    copy_file(
        ctx,
        ctx.grafana_assets_dir / "dashboards" / "sglang-overview.json",
        ctx.grafana_dashboard_dir / "sglang-overview.json",
        mode=0o644,
        owner="grafana",
        group="grafana",
    )


def wait_for_grafana(ctx, timeout=90):
    if ctx.dry_run:
        return
    deadline = time.time() + timeout
    url = ctx.grafana_url + "/api/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Grafana did not become healthy at {0}".format(url))


def set_admin_password(ctx):
    ctx.ensure_grafana_admin_password()
    if ctx.dry_run:
        LOG.info("[dry-run] reset Grafana admin password")
        return
    if command_exists("grafana"):
        cmd = [
            "grafana",
            "cli",
            "--homepath",
            "/usr/share/grafana",
            "--config",
            "/etc/grafana/grafana.ini",
            "admin",
            "reset-admin-password",
            ctx.grafana_admin_password,
        ]
    elif command_exists("grafana-cli"):
        cmd = ["grafana-cli", "admin", "reset-admin-password", ctx.grafana_admin_password]
    else:
        raise RuntimeError("grafana-cli was not found after installing Grafana")
    run(ctx, cmd, secrets=[ctx.grafana_admin_password])


def grafana_api(ctx, path, method="GET", data=None):
    url = ctx.grafana_url + path
    encoded = None
    headers = {}
    if data is not None:
        encoded = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    token = "{0}:{1}".format(ctx.grafana_admin_user, ctx.grafana_admin_password).encode("utf-8")
    headers["Authorization"] = "Basic " + base64.b64encode(token).decode("ascii")
    req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            return response.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
