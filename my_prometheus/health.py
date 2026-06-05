import base64
import json
import logging
import time
import urllib.error
import urllib.request

from .command import run


LOG = logging.getLogger(__name__)


def http_get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", "replace")


def wait_http(url, expected=(200,), timeout=90):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            status, body = http_get(url, timeout=5)
            if status in expected:
                return status, body
            last_error = "HTTP {0}".format(status)
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError("{0} not healthy: {1}".format(url, last_error))


def check_service(ctx, service):
    proc = run(ctx, ["systemctl", "is-active", service], check=False, capture=True)
    status = (proc.stdout or "").strip()
    if status != "active":
        raise RuntimeError("service is not active: {0} ({1})".format(service, status))
    LOG.info("service active: %s", service)


def check_prometheus_targets(ctx):
    deadline = time.time() + 90
    last_labels = {}
    while time.time() < deadline:
        status, body = wait_http(ctx.prometheus_url + "/api/v1/targets", timeout=10)
        data = json.loads(body)
        active = data.get("data", {}).get("activeTargets", [])
        labels = {}
        for target in active:
            job = target.get("labels", {}).get("job")
            health = target.get("health")
            labels[job] = health
        if labels.get("prometheus") == "up" and labels.get("node_exporter") == "up":
            LOG.info("Prometheus targets are up: prometheus, node_exporter")
            return
        last_labels = labels
        time.sleep(3)
    raise RuntimeError("Prometheus targets are not up: {0}".format(last_labels))


def check_grafana_datasource(ctx):
    if not ctx.grafana_admin_password:
        LOG.info("Grafana datasource auth check skipped; admin password is unchanged and not known")
        return
    token = "{0}:{1}".format(ctx.grafana_admin_user, ctx.grafana_admin_password).encode("utf-8")
    headers = {
        "Authorization": "Basic " + base64.b64encode(token).decode("ascii"),
    }
    req = urllib.request.Request(
        ctx.grafana_url + "/api/datasources/name/Prometheus",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Grafana Prometheus datasource check failed: HTTP {0}".format(exc.code))
    data = json.loads(body)
    if data.get("type") != "prometheus":
        raise RuntimeError("Grafana datasource Prometheus has unexpected type: {0}".format(data.get("type")))
    LOG.info("Grafana datasource exists: Prometheus")


def run_health_checks(ctx):
    if ctx.dry_run:
        LOG.info("[dry-run] skip health checks")
        return
    for service in ctx.service_list():
        check_service(ctx, service)
    wait_http(ctx.prometheus_url + "/-/ready", timeout=60)
    wait_http(ctx.node_exporter_url + "/metrics", timeout=60)
    wait_http(ctx.grafana_url + "/api/health", timeout=90)
    if ctx.with_alertmanager:
        wait_http(ctx.alertmanager_url + "/-/ready", timeout=60)
    check_prometheus_targets(ctx)
    check_grafana_datasource(ctx)


def print_summary(ctx):
    host = ctx.server_ip or "127.0.0.1"
    print("")
    print("Installation completed.")
    print("Prometheus: http://{0}:{1}".format(host, ctx.prometheus_port))
    print("Grafana:    http://{0}:{1}".format(host, ctx.grafana_port))
    print("Node Exporter: http://127.0.0.1:{0}".format(ctx.node_exporter_port))
    if ctx.with_alertmanager:
        print("Alertmanager: http://{0}:{1}".format(host, ctx.alertmanager_port))
    print("Grafana user: {0}".format(ctx.grafana_admin_user))
    if ctx.grafana_password_changed:
        print("Grafana password: {0}".format(ctx.grafana_admin_password))
        if ctx.generated_grafana_password:
            print("Grafana generated credential file: {0}".format(ctx.grafana_credentials_file))
    else:
        print("Grafana password: unchanged; use --reset-grafana-admin-password to reset it")
    print("Config: {0}".format(ctx.config_dir / "prometheus.yml"))
    print("Data: {0}".format(ctx.prometheus_data_dir))
    print("Logs: journalctl -u {0}".format(" -u ".join(ctx.service_list())))
