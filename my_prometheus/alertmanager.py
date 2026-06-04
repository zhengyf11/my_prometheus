import logging

from .download import download_file, extract_tarball, github_release_tar_url, install_binary, version_number
from .files import ensure_dir, render_template, write_managed_file
from .systemd import daemon_reload, enable_now, restart, write_service
from .users import ensure_system_user


LOG = logging.getLogger(__name__)


def alertmanager_asset(ctx):
    return "alertmanager-{0}.linux-{1}.tar.gz".format(
        version_number(ctx.alertmanager_version), ctx.prometheus_arch
    )


def install_alertmanager(ctx):
    LOG.info("installing Alertmanager %s", ctx.alertmanager_version)
    ensure_system_user(ctx, "alertmanager")
    ensure_dir(ctx, ctx.install_dir)
    ensure_dir(ctx, ctx.download_dir)
    ensure_dir(ctx, ctx.alertmanager_config_dir, owner="alertmanager", group="alertmanager")
    ensure_dir(ctx, ctx.alertmanager_data_dir, owner="alertmanager", group="alertmanager")

    asset = alertmanager_asset(ctx)
    url = github_release_tar_url("alertmanager", ctx.alertmanager_version, asset)
    tarball = download_file(ctx, url, ctx.download_dir / asset)
    extracted = extract_tarball(ctx, tarball, ctx.install_dir)
    install_binary(ctx, extracted / "alertmanager", "alertmanager")
    install_binary(ctx, extracted / "amtool", "amtool")

    content = render_template(ctx, "alertmanager.yml.tpl", {})
    write_managed_file(
        ctx,
        ctx.alertmanager_config_dir / "alertmanager.yml",
        content,
        owner="alertmanager",
        group="alertmanager",
    )

    service_changed = write_service(
        ctx,
        "alertmanager.service",
        "alertmanager.service.tpl",
        {
            "bin_dir": ctx.bin_dir,
            "config_file": ctx.alertmanager_config_dir / "alertmanager.yml",
            "data_dir": ctx.alertmanager_data_dir,
            "listen_address": ctx.listen_address,
            "alertmanager_port": ctx.alertmanager_port,
        },
    )
    if service_changed:
        daemon_reload(ctx)
    enable_now(ctx, "alertmanager")
    restart(ctx, "alertmanager")
