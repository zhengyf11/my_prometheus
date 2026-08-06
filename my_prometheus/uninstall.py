import argparse
import filecmp
import json
import logging
import os
import shutil
from pathlib import Path

from .command import command_exists, run
from .files import MANAGED_MARKER, read_text
from . import __version__


LOG = logging.getLogger(__name__)

SERVICES = ("prometheus", "node_exporter", "grafana-server", "alertmanager")
CUSTOM_SERVICES = ("prometheus", "node_exporter", "alertmanager")
BINARIES = ("prometheus", "promtool", "node_exporter", "alertmanager", "amtool")


class UninstallContext(object):
    def __init__(self, args):
        self.yes = args.yes
        self.dry_run = args.dry_run
        self.force = args.force
        self.purge_data = args.purge_data
        self.remove_grafana = args.remove_grafana
        self.keep_grafana = args.keep_grafana
        self.remove_firewall_rules = args.remove_firewall_rules
        self.command_timeout = args.command_timeout
        self.proxy = None

        self.install_dir = Path(args.install_dir)
        self.config_dir = Path(args.config_dir)
        self.prometheus_data_dir = Path(args.prometheus_data_dir)
        self.state_dir = Path(args.state_dir)
        self.state_file = self.state_dir / "install-state.json"
        self.bin_dir = Path(args.bin_dir)
        self.systemd_dir = Path("/etc/systemd/system")
        self.alertmanager_config_dir = Path("/etc/alertmanager")
        self.alertmanager_data_dir = Path("/var/lib/alertmanager")
        self.grafana_data_dir = Path("/var/lib/grafana")
        self.grafana_ini = Path("/etc/grafana/grafana.ini")
        self.grafana_provisioning_dir = Path("/etc/grafana/provisioning")
        self.grafana_dashboard = Path("/var/lib/grafana/dashboards/linux/node-overview.json")
        self.sglang_dashboards = [
            Path("/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json"),
            Path("/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json"),
            Path("/var/lib/grafana/dashboards/sglang/sglang-router.json"),
        ]
        self.repo_root = Path(__file__).resolve().parent.parent
        self.dashboard_source = self.repo_root / "grafana/dashboards/node-overview.json"
        self.sglang_dashboard_sources = [
            self.repo_root / "grafana/dashboards/sglang-pd-unified.json",
            self.repo_root / "grafana/dashboards/sglang-pd-disaggregated.json",
            self.repo_root / "grafana/dashboards/sglang-router.json",
        ]

        self.prometheus_port = args.prometheus_port
        self.grafana_port = args.grafana_port
        self.alertmanager_port = args.alertmanager_port


def build_parser():
    parser = argparse.ArgumentParser(
        description="Uninstall services and files managed by my_prometheus."
    )
    parser.add_argument("--version", action="version", version="my_prometheus {0}".format(__version__))
    parser.add_argument("--install-dir", default="/opt/my_prometheus")
    parser.add_argument("--config-dir", default="/etc/prometheus")
    parser.add_argument("--prometheus-data-dir", default="/var/lib/prometheus")
    parser.add_argument("--state-dir", default="/var/lib/my_prometheus")
    parser.add_argument("--bin-dir", default="/usr/local/bin")
    parser.add_argument("--prometheus-port", type=int, default=9090)
    parser.add_argument("--grafana-port", type=int, default=3000)
    parser.add_argument("--alertmanager-port", type=int, default=9093)
    grafana_group = parser.add_mutually_exclusive_group()
    grafana_group.add_argument("--remove-grafana", action="store_true")
    grafana_group.add_argument("--keep-grafana", action="store_true")
    parser.add_argument("--purge-data", action="store_true")
    parser.add_argument("--remove-firewall-rules", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", "-y", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--command-timeout", type=int, default=600)
    return parser


def configure_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def confirm(ctx):
    if ctx.yes or ctx.dry_run:
        return
    suffix = " Data directories will also be deleted." if ctx.purge_data else ""
    answer = input("Uninstall the my_prometheus monitoring stack?{0} [y/N] ".format(suffix))
    if answer.strip().lower() not in ("y", "yes"):
        raise RuntimeError("cancelled by user")


def require_root(ctx):
    if ctx.dry_run:
        return
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        raise RuntimeError("please run as root, for example: sudo python3 uninstall.py")


def managed(path):
    path = Path(path)
    if not path.is_file():
        return False
    try:
        return MANAGED_MARKER in read_text(path)
    except (OSError, UnicodeDecodeError):
        return False


def remove_path(ctx, path, recursive=False):
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return
    if ctx.dry_run:
        LOG.info("[dry-run] remove %s", path)
        return
    if recursive and path.is_dir() and not path.is_symlink():
        shutil.rmtree(str(path))
    elif path.is_dir() and not path.is_symlink():
        try:
            path.rmdir()
        except OSError:
            return
    else:
        path.unlink()
    LOG.info("removed %s", path)


def remove_managed_file(ctx, path):
    path = Path(path)
    if not path.exists():
        return False
    if not managed(path) and not ctx.force:
        LOG.warning("preserving unmanaged file %s; use --force to remove it", path)
        return False
    remove_path(ctx, path)
    return True


def stop_services(ctx):
    for service in SERVICES:
        run(ctx, ["systemctl", "disable", "--now", service], check=False, capture=True)
    running = []
    for service in SERVICES:
        result = run(ctx, ["systemctl", "is-active", service], check=False, capture=True)
        status = (result.stdout or "").strip()
        if status in ("active", "activating", "reloading", "deactivating"):
            running.append("{0} ({1})".format(service, status))
    if running:
        raise RuntimeError("services did not stop: {0}".format(", ".join(running)))


def remove_custom_services(ctx):
    for service in CUSTOM_SERVICES:
        remove_managed_file(ctx, ctx.systemd_dir / (service + ".service"))
    run(ctx, ["systemctl", "daemon-reload"], check=False)
    run(ctx, ["systemctl", "reset-failed"], check=False)


def has_install_evidence(ctx):
    if ctx.state_file.exists():
        return True
    return any(managed(ctx.systemd_dir / (name + ".service")) for name in CUSTOM_SERVICES)


def remove_binaries(ctx):
    if not has_install_evidence(ctx) and not ctx.force:
        raise RuntimeError(
            "installation state and managed service files were not found; use --force to remove binaries"
        )
    for name in BINARIES:
        remove_path(ctx, ctx.bin_dir / name)


def remove_prometheus_config(ctx):
    remove_managed_file(ctx, ctx.config_dir / "prometheus.yml")
    remove_managed_file(ctx, ctx.config_dir / "rules/default.yml")
    remove_managed_file(ctx, ctx.config_dir / "targets/nodes.yml")
    remove_path(ctx, ctx.config_dir / "rules")
    remove_path(ctx, ctx.config_dir / "targets")
    remove_path(ctx, ctx.config_dir)


def remove_alertmanager_config(ctx):
    remove_managed_file(ctx, ctx.alertmanager_config_dir / "alertmanager.yml")
    remove_path(ctx, ctx.alertmanager_config_dir)


def restore_oldest_backup(ctx, path):
    path = Path(path)
    backups = sorted(path.parent.glob(path.name + ".bak.*"))
    if not backups:
        return False
    backup = backups[0]
    if ctx.dry_run:
        LOG.info("[dry-run] restore %s from %s", path, backup)
        return True
    shutil.copy2(str(backup), str(path))
    LOG.info("restored %s from %s", path, backup)
    return True


def remove_grafana_files(ctx):
    remove_managed_file(
        ctx, ctx.grafana_provisioning_dir / "datasources/prometheus.yml"
    )
    remove_managed_file(
        ctx, ctx.grafana_provisioning_dir / "dashboards/dashboards.yml"
    )
    remove_dashboard(ctx, ctx.dashboard_source, ctx.grafana_dashboard)
    for source, destination in zip(
        ctx.sglang_dashboard_sources, ctx.sglang_dashboards
    ):
        remove_dashboard(ctx, source, destination)
    restore_oldest_backup(ctx, ctx.grafana_ini)


def remove_dashboard(ctx, source, destination):
    if destination.exists():
        unchanged = (
            source.exists()
            and filecmp.cmp(
                str(source), str(destination), shallow=False
            )
        )
        if unchanged or ctx.force:
            remove_path(ctx, destination)
        else:
            LOG.warning("preserving modified dashboard %s", destination)


def remove_grafana_package(ctx):
    if not should_remove_grafana(ctx):
        return
    if command_exists("apt-get"):
        run(ctx, ["apt-get", "-y", "remove", "grafana"], check=False)
    elif command_exists("dnf"):
        run(ctx, ["dnf", "-y", "remove", "grafana"], check=False)
    elif command_exists("yum"):
        run(ctx, ["yum", "-y", "remove", "grafana"], check=False)


def read_install_state(ctx):
    if not ctx.state_file.exists():
        return {}
    try:
        with open(str(ctx.state_file), "r") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        LOG.warning("failed to read install state %s: %s", ctx.state_file, exc)
        return {}


def should_remove_grafana(ctx):
    if ctx.keep_grafana:
        LOG.info("Grafana package preserved by --keep-grafana")
        return False
    if ctx.remove_grafana:
        return True
    preexisting = read_install_state(ctx).get("grafana_preexisting")
    if preexisting is False:
        return True
    if preexisting is True:
        LOG.info("Grafana package preserved because it existed before installation")
    else:
        LOG.info("Grafana package ownership is unknown; use --remove-grafana to remove it")
    return False


def remove_grafana_repo(ctx):
    apt_source = Path("/etc/apt/sources.list.d/grafana.list")
    if managed(apt_source) or ctx.force:
        remove_path(ctx, apt_source)
        remove_path(ctx, "/etc/apt/keyrings/grafana.asc")
    remove_managed_file(ctx, "/etc/yum.repos.d/grafana.repo")


def remove_firewall_rules(ctx):
    if not ctx.remove_firewall_rules:
        return
    ports = (ctx.prometheus_port, ctx.grafana_port, ctx.alertmanager_port)
    if command_exists("firewall-cmd"):
        for port in ports:
            run(
                ctx,
                ["firewall-cmd", "--remove-port={0}/tcp".format(port), "--permanent"],
                check=False,
            )
        run(ctx, ["firewall-cmd", "--reload"], check=False)
    elif command_exists("ufw"):
        for port in ports:
            run(ctx, ["ufw", "--force", "delete", "allow", "{0}/tcp".format(port)], check=False)


def purge_data(ctx):
    if not ctx.purge_data:
        LOG.info("data directories preserved; use --purge-data to remove them")
        return
    for path in (
        ctx.prometheus_data_dir,
        ctx.alertmanager_data_dir,
        ctx.grafana_data_dir,
    ):
        remove_path(ctx, path, recursive=True)
    for user in ("prometheus", "node_exporter", "alertmanager"):
        run(ctx, ["userdel", user], check=False, capture=True)


def uninstall(ctx):
    stop_services(ctx)
    remove_binaries(ctx)
    remove_custom_services(ctx)
    remove_prometheus_config(ctx)
    remove_alertmanager_config(ctx)
    remove_grafana_files(ctx)
    remove_grafana_package(ctx)
    remove_grafana_repo(ctx)
    remove_firewall_rules(ctx)
    remove_path(ctx, ctx.install_dir, recursive=True)
    purge_data(ctx)
    remove_path(ctx, ctx.state_dir, recursive=True)
    LOG.info("uninstall completed")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    ctx = UninstallContext(args)
    try:
        confirm(ctx)
        require_root(ctx)
        uninstall(ctx)
        return 0
    except KeyboardInterrupt:
        LOG.error("cancelled")
        return 130
    except Exception as exc:
        LOG.error("%s", exc)
        if args.verbose:
            LOG.exception("uninstaller failed")
        return 1
