import logging

from .command import run
from .files import render_template, write_managed_file


LOG = logging.getLogger(__name__)


def write_service(ctx, service_name, template_name, values):
    content = render_template(ctx, template_name, values)
    path = ctx.systemd_dir / service_name
    changed = write_managed_file(ctx, path, content, mode=0o644)
    return changed


def daemon_reload(ctx):
    run(ctx, ["systemctl", "daemon-reload"])


def enable_now(ctx, service):
    run(ctx, ["systemctl", "enable", "--now", service])


def restart(ctx, service):
    run(ctx, ["systemctl", "restart", service])


def reload_or_restart(ctx, service):
    proc = run(ctx, ["systemctl", "reload", service], check=False, capture=True)
    if proc.returncode != 0:
        restart(ctx, service)


def is_active(ctx, service):
    proc = run(ctx, ["systemctl", "is-active", service], check=False, capture=True)
    return (proc.stdout or "").strip() == "active"
