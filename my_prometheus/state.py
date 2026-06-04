import json
import logging
import time

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
        "with_alertmanager": ctx.with_alertmanager,
        "config_dir": str(ctx.config_dir),
        "prometheus_data_dir": str(ctx.prometheus_data_dir),
    }
    write_text_atomic(ctx.state_file, json.dumps(state, indent=2, sort_keys=True) + "\n", mode=0o600)
    LOG.info("wrote state %s", ctx.state_file)
