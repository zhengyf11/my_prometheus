import logging

from .download import download_file, extract_tarball, github_release_tar_url, install_binary, version_number
from .files import ensure_dir
from .packages import ensure_base_packages
from .systemd import daemon_reload, enable_now, restart, write_service
from .users import ensure_system_user


LOG = logging.getLogger(__name__)


def node_exporter_asset(ctx):
    return "node_exporter-{0}.linux-{1}.tar.gz".format(
        version_number(ctx.node_exporter_version), ctx.prometheus_arch
    )


def install_node_exporter(ctx):
    LOG.info("installing Node Exporter %s", ctx.node_exporter_version)
    ensure_base_packages(ctx)
    ensure_system_user(ctx, "node_exporter")
    ensure_dir(ctx, ctx.install_dir)
    ensure_dir(ctx, ctx.download_dir)

    asset = node_exporter_asset(ctx)
    url = github_release_tar_url("node_exporter", ctx.node_exporter_version, asset)
    tarball = download_file(ctx, url, ctx.download_dir / asset)
    extracted = extract_tarball(ctx, tarball, ctx.install_dir)
    install_binary(ctx, extracted / "node_exporter", "node_exporter")

    service_changed = write_service(
        ctx,
        "node_exporter.service",
        "node_exporter.service.tpl",
        {
            "bin_dir": ctx.bin_dir,
            "listen_address": "127.0.0.1",
            "node_exporter_port": ctx.node_exporter_port,
        },
    )
    if service_changed:
        daemon_reload(ctx)
    enable_now(ctx, "node_exporter")
    restart(ctx, "node_exporter")
