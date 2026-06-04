import argparse
import logging

from .context import (
    DEFAULT_ALERTMANAGER_VERSION,
    DEFAULT_NODE_EXPORTER_VERSION,
    DEFAULT_PROMETHEUS_VERSION,
    InstallContext,
    env_bool,
    env_default,
)
from .detect import preflight
from .firewall import configure_firewall
from .grafana import install_grafana
from .health import print_summary, run_health_checks
from .node_exporter import install_node_exporter
from .alertmanager import install_alertmanager
from .prometheus import install_prometheus
from .state import write_state


LOG = logging.getLogger(__name__)


def parse_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in ("1", "true", "yes", "y", "on"):
        return True
    if normalized in ("0", "false", "no", "n", "off"):
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Install Prometheus, Node Exporter, Grafana, and optional Alertmanager."
    )
    parser.add_argument(
        "--prometheus-version",
        default=env_default("PROMETHEUS_VERSION", DEFAULT_PROMETHEUS_VERSION),
    )
    parser.add_argument(
        "--node-exporter-version",
        default=env_default("NODE_EXPORTER_VERSION", DEFAULT_NODE_EXPORTER_VERSION),
    )
    parser.add_argument(
        "--alertmanager-version",
        default=env_default("ALERTMANAGER_VERSION", DEFAULT_ALERTMANAGER_VERSION),
    )
    parser.add_argument(
        "--grafana-version",
        default=env_default("GRAFANA_VERSION", "latest"),
        help="Grafana package version or latest.",
    )
    parser.add_argument(
        "--grafana-admin-user",
        default=env_default("GRAFANA_ADMIN_USER", "admin"),
    )
    parser.add_argument(
        "--grafana-admin-password",
        default=env_default("GRAFANA_ADMIN_PASSWORD", None),
    )
    parser.add_argument("--listen-address", default=env_default("LISTEN_ADDRESS", "0.0.0.0"))
    parser.add_argument("--prometheus-port", type=int, default=int(env_default("PROMETHEUS_PORT", "9090")))
    parser.add_argument("--node-exporter-port", type=int, default=int(env_default("NODE_EXPORTER_PORT", "9100")))
    parser.add_argument("--grafana-port", type=int, default=int(env_default("GRAFANA_PORT", "3000")))
    parser.add_argument("--alertmanager-port", type=int, default=int(env_default("ALERTMANAGER_PORT", "9093")))
    parser.add_argument("--retention-time", default=env_default("RETENTION_TIME", "15d"))
    parser.add_argument("--install-dir", default=env_default("INSTALL_DIR", "/opt/my_prometheus"))
    parser.add_argument("--download-dir", default=env_default("DOWNLOAD_DIR", "/opt/my_prometheus/downloads"))
    parser.add_argument("--config-dir", default=env_default("CONFIG_DIR", "/etc/prometheus"))
    parser.add_argument("--prometheus-data-dir", default=env_default("PROMETHEUS_DATA_DIR", "/var/lib/prometheus"))
    parser.add_argument("--state-dir", default=env_default("STATE_DIR", "/var/lib/my_prometheus"))
    parser.add_argument("--bin-dir", default=env_default("BIN_DIR", "/usr/local/bin"))
    parser.add_argument("--with-alertmanager", type=parse_bool, default=env_bool("WITH_ALERTMANAGER", False))
    parser.add_argument("--open-firewall", type=parse_bool, default=env_bool("OPEN_FIREWALL", True))
    parser.add_argument("--skip-network-check", action="store_true")
    parser.add_argument("--download-timeout", type=int, default=int(env_default("DOWNLOAD_TIMEOUT", "300")))
    parser.add_argument("--download-retries", type=int, default=int(env_default("DOWNLOAD_RETRIES", "3")))
    parser.add_argument("--command-timeout", type=int, default=int(env_default("COMMAND_TIMEOUT", "600")))
    parser.add_argument("--force", action="store_true", help="Replace unrelated files after backing them up.")
    parser.add_argument("--yes", "-y", action="store_true", help="Run without confirmation.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without changing the system.")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser


def configure_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def confirm(ctx):
    if ctx.yes or ctx.dry_run:
        return
    message = (
        "This will install and configure Prometheus, Node Exporter and Grafana "
        "on this host. Continue? [y/N] "
    )
    answer = input(message)
    if answer.strip().lower() not in ("y", "yes"):
        raise RuntimeError("cancelled by user")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    ctx = InstallContext(args)

    try:
        confirm(ctx)
        preflight(ctx)
        install_node_exporter(ctx)
        install_prometheus(ctx)
        if ctx.with_alertmanager:
            install_alertmanager(ctx)
        install_grafana(ctx)
        configure_firewall(ctx)
        write_state(ctx)
        run_health_checks(ctx)
        print_summary(ctx)
        return 0
    except KeyboardInterrupt:
        LOG.error("cancelled")
        return 130
    except Exception as exc:
        LOG.error("%s", exc)
        if ctx.verbose:
            LOG.exception("installer failed")
        return 1
