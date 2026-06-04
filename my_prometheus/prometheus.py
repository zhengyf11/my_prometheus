import logging

from .command import run
from .download import download_file, extract_tarball, github_release_tar_url, install_binary, version_number
from .files import ensure_dir, render_template, write_managed_file
from .packages import ensure_base_packages
from .systemd import daemon_reload, enable_now, restart, write_service
from .users import ensure_system_user


LOG = logging.getLogger(__name__)


def prometheus_asset(ctx):
    return "prometheus-{0}.linux-{1}.tar.gz".format(version_number(ctx.prometheus_version), ctx.prometheus_arch)


def install_prometheus(ctx):
    LOG.info("installing Prometheus %s", ctx.prometheus_version)
    ensure_base_packages(ctx)
    ensure_system_user(ctx, "prometheus")
    ensure_dir(ctx, ctx.install_dir)
    ensure_dir(ctx, ctx.download_dir)
    ensure_dir(ctx, ctx.config_dir, owner="prometheus", group="prometheus")
    ensure_dir(ctx, ctx.targets_dir, owner="prometheus", group="prometheus")
    ensure_dir(ctx, ctx.rules_dir, owner="prometheus", group="prometheus")
    ensure_dir(ctx, ctx.prometheus_data_dir, owner="prometheus", group="prometheus")

    asset = prometheus_asset(ctx)
    url = github_release_tar_url("prometheus", ctx.prometheus_version, asset)
    tarball = download_file(ctx, url, ctx.download_dir / asset)
    extracted = extract_tarball(ctx, tarball, ctx.install_dir)
    install_binary(ctx, extracted / "prometheus", "prometheus")
    install_binary(ctx, extracted / "promtool", "promtool")

    alerting_config = ""
    if ctx.with_alertmanager:
        alerting_config = """\nalerting:\n  alertmanagers:\n    - static_configs:\n        - targets:\n            - localhost:{0}\n""".format(ctx.alertmanager_port)

    content = render_template(
        ctx,
        "prometheus.yml.tpl",
        {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
            "prometheus_port": ctx.prometheus_port,
            "node_exporter_port": ctx.node_exporter_port,
            "rules_dir": ctx.rules_dir,
            "targets_dir": ctx.targets_dir,
            "alerting_config": alerting_config,
        },
    )
    write_managed_file(ctx, ctx.config_dir / "prometheus.yml", content, owner="prometheus", group="prometheus")

    nodes = render_template(
        ctx,
        "nodes.yml.tpl",
        {
            "node_exporter_port": ctx.node_exporter_port,
        },
    )
    write_managed_file(ctx, ctx.targets_dir / "nodes.yml", nodes, owner="prometheus", group="prometheus")
    rules = render_template(ctx, "rules.yml.tpl", {})
    write_managed_file(ctx, ctx.rules_dir / "default.yml", rules, owner="prometheus", group="prometheus")

    service_changed = write_service(
        ctx,
        "prometheus.service",
        "prometheus.service.tpl",
        {
            "bin_dir": ctx.bin_dir,
            "config_file": ctx.config_dir / "prometheus.yml",
            "data_dir": ctx.prometheus_data_dir,
            "retention_time": ctx.retention_time,
            "listen_address": ctx.listen_address,
            "prometheus_port": ctx.prometheus_port,
        },
    )
    if service_changed:
        daemon_reload(ctx)

    run(ctx, [str(ctx.bin_dir / "promtool"), "check", "config", str(ctx.config_dir / "prometheus.yml")])
    enable_now(ctx, "prometheus")
    restart(ctx, "prometheus")
