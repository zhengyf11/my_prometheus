import json
import logging
import time
from pathlib import Path

from .files import ensure_dir, write_text_atomic


LOG = logging.getLogger(__name__)


def write_state(ctx):
    if ctx.dry_run:
        LOG.info("[dry-run] write state %s", ctx.state_file)
        return
    ensure_dir(ctx, ctx.state_dir, mode=0o700)
    state = {
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prometheus_version": ctx.prometheus_version,
        "node_exporter_version": ctx.node_exporter_version,
        "alertmanager_version": ctx.alertmanager_version if ctx.with_alertmanager else None,
        "grafana_version": ctx.grafana_version,
        "grafana_admin_user": ctx.grafana_admin_user,
        "grafana_admin_password_initialized": ctx.grafana_password_changed,
        "grafana_preexisting": ctx.grafana_preexisting,
        "with_alertmanager": ctx.with_alertmanager,
        "config_dir": str(ctx.config_dir),
        "prometheus_data_dir": str(ctx.prometheus_data_dir),
    }
    write_text_atomic(ctx.state_file, json.dumps(state, indent=2, sort_keys=True) + "\n", mode=0o600)
    LOG.info("wrote state %s", ctx.state_file)


def read_state(ctx):
    path = Path(ctx.state_file)
    if not path.exists():
        return {}
    try:
        with open(str(path), "r") as handle:
            return json.load(handle)
    except Exception as exc:
        LOG.warning("failed to read state %s: %s", path, exc)
        return {}


def write_grafana_credentials(ctx):
    if not ctx.grafana_admin_password:
        return
    if ctx.dry_run:
        LOG.info("[dry-run] write Grafana credentials %s", ctx.grafana_credentials_file)
        return
    ensure_dir(ctx, ctx.state_dir, mode=0o700)
    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user": ctx.grafana_admin_user,
        "password": ctx.grafana_admin_password,
    }
    write_text_atomic(
        ctx.grafana_credentials_file,
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        mode=0o600,
    )
    LOG.info("wrote generated Grafana credentials to %s", ctx.grafana_credentials_file)


def read_grafana_credentials(ctx):
    path = Path(ctx.grafana_credentials_file)
    if not path.exists():
        return {}
    try:
        with open(str(path), "r") as handle:
            data = json.load(handle)
        if data.get("user") != ctx.grafana_admin_user:
            return {}
        return data
    except Exception as exc:
        LOG.warning("failed to read Grafana credentials %s: %s", path, exc)
        return {}
