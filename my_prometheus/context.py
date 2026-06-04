import os
import secrets
import string
from pathlib import Path


DEFAULT_PROMETHEUS_VERSION = "3.12.0"
DEFAULT_NODE_EXPORTER_VERSION = "1.11.1"
DEFAULT_ALERTMANAGER_VERSION = "0.32.1"


class InstallContext(object):
    def __init__(self, args):
        self.prometheus_version = args.prometheus_version
        self.node_exporter_version = args.node_exporter_version
        self.alertmanager_version = args.alertmanager_version
        self.grafana_version = args.grafana_version
        self.grafana_admin_user = args.grafana_admin_user
        self.grafana_admin_password = args.grafana_admin_password or generate_password()
        self.generated_grafana_password = args.grafana_admin_password is None
        self.listen_address = args.listen_address
        self.prometheus_port = args.prometheus_port
        self.node_exporter_port = args.node_exporter_port
        self.grafana_port = args.grafana_port
        self.alertmanager_port = args.alertmanager_port
        self.retention_time = args.retention_time
        self.with_alertmanager = args.with_alertmanager
        self.open_firewall = args.open_firewall
        self.yes = args.yes
        self.dry_run = args.dry_run
        self.verbose = args.verbose
        self.skip_network_check = args.skip_network_check
        self.force = args.force
        self.download_timeout = args.download_timeout
        self.download_retries = args.download_retries
        self.command_timeout = args.command_timeout

        self.install_dir = Path(args.install_dir)
        self.download_dir = Path(args.download_dir)
        self.config_dir = Path(args.config_dir)
        self.targets_dir = self.config_dir / "targets"
        self.rules_dir = self.config_dir / "rules"
        self.prometheus_data_dir = Path(args.prometheus_data_dir)
        self.state_dir = Path(args.state_dir)
        self.state_file = self.state_dir / "install-state.json"
        self.bin_dir = Path(args.bin_dir)
        self.systemd_dir = Path("/etc/systemd/system")
        self.grafana_provisioning_dir = Path("/etc/grafana/provisioning")
        self.grafana_dashboard_dir = Path("/var/lib/grafana/dashboards")
        self.alertmanager_config_dir = Path("/etc/alertmanager")
        self.alertmanager_data_dir = Path("/var/lib/alertmanager")

        self.repo_root = Path(__file__).resolve().parent.parent
        self.templates_dir = self.repo_root / "templates"
        self.grafana_assets_dir = self.repo_root / "grafana"

        self.os_info = {}
        self.arch = None
        self.prometheus_arch = None
        self.package_manager = None
        self.server_ip = None

    @property
    def prometheus_url(self):
        return "http://localhost:{0}".format(self.prometheus_port)

    @property
    def node_exporter_url(self):
        return "http://localhost:{0}".format(self.node_exporter_port)

    @property
    def grafana_url(self):
        return "http://localhost:{0}".format(self.grafana_port)

    @property
    def alertmanager_url(self):
        return "http://localhost:{0}".format(self.alertmanager_port)

    def service_list(self):
        services = ["prometheus", "node_exporter", "grafana-server"]
        if self.with_alertmanager:
            services.append("alertmanager")
        return services


def env_default(name, default):
    return os.environ.get(name, default)


def env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def generate_password(length=18):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
