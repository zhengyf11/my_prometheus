import logging
import os
import platform
import socket

from .command import command_exists, run, run_output
from .download import open_url


LOG = logging.getLogger(__name__)


SUPPORTED_ID_LIKE = ("rhel", "fedora", "centos", "debian", "ubuntu")
ARCH_MAP = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


def read_os_release():
    result = {}
    path = "/etc/os-release"
    if not os.path.exists(path):
        return result
    with open(path, "r") as handle:
        for line in handle:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            result[key] = value.strip().strip('"')
    return result


def require_root(ctx):
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        raise RuntimeError("please run as root, for example: sudo python3 install.py")


def detect_package_manager():
    if command_exists("dnf"):
        return "dnf"
    if command_exists("yum"):
        return "yum"
    if command_exists("apt-get"):
        return "apt-get"
    raise RuntimeError("dnf, yum or apt-get was not found")


def detect_arch():
    arch = platform.machine().lower()
    if arch not in ARCH_MAP:
        raise RuntimeError("unsupported CPU architecture: {0}".format(arch))
    return arch, ARCH_MAP[arch]


def check_os(ctx):
    info = read_os_release()
    os_id = info.get("ID", "").lower()
    id_like = info.get("ID_LIKE", "").lower().split()
    candidates = [os_id] + id_like
    if not any(item in SUPPORTED_ID_LIKE for item in candidates):
        raise RuntimeError("unsupported OS: {0}".format(info.get("PRETTY_NAME", "unknown")))
    ctx.os_info = info
    LOG.info("OS: %s", info.get("PRETTY_NAME", "unknown"))


def check_systemd(ctx):
    if not os.path.isdir("/run/systemd/system") or not command_exists("systemctl"):
        raise RuntimeError("systemd is required")
    run(ctx, ["systemctl", "--version"], check=True, capture=True)


def port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(0.4)
        return sock.connect_ex(("127.0.0.1", int(port))) == 0
    finally:
        sock.close()


def check_ports(ctx):
    checks = [
        ("Prometheus", ctx.prometheus_port, "prometheus"),
        ("Node Exporter", ctx.node_exporter_port, "node_exporter"),
        ("Grafana", ctx.grafana_port, "grafana-server"),
    ]
    if ctx.with_alertmanager:
        checks.append(("Alertmanager", ctx.alertmanager_port, "alertmanager"))

    for name, port, service in checks:
        if not port_in_use(port):
            continue
        active = run(ctx, ["systemctl", "is-active", service], check=False, capture=True)
        if (active.stdout or "").strip() == "active":
            LOG.info("%s port %s is already used by %s; treating as existing install", name, port, service)
            continue
        if not ctx.force:
            raise RuntimeError(
                "{0} port {1} is already in use. Stop the process or rerun with --force.".format(name, port)
            )


def check_network(ctx):
    if ctx.skip_network_check:
        LOG.info("network preflight skipped")
        return
    grafana_url = (
        "https://apt.grafana.com/"
        if ctx.package_manager == "apt-get"
        else "https://rpm.grafana.com/"
    )
    urls = ["https://github.com/prometheus/prometheus/releases/", grafana_url]
    for url in urls:
        try:
            with open_url(ctx, url, timeout=10) as response:
                if response.status >= 400:
                    raise RuntimeError("unexpected HTTP status {0}".format(response.status))
        except Exception as exc:
            raise RuntimeError("network check failed for {0}: {1}".format(url, exc))


def detect_server_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        sock.close()


def log_selinux(ctx):
    if not command_exists("getenforce"):
        return
    proc = run(ctx, ["getenforce"], check=False, capture=True)
    status = (proc.stdout or "").strip()
    if status:
        LOG.info("SELinux: %s", status)


def preflight(ctx):
    require_root(ctx)
    check_os(ctx)
    ctx.package_manager = detect_package_manager()
    ctx.arch, ctx.prometheus_arch = detect_arch()
    ctx.server_ip = detect_server_ip()
    LOG.info("package manager: %s", ctx.package_manager)
    LOG.info("architecture: %s -> %s", ctx.arch, ctx.prometheus_arch)
    check_systemd(ctx)
    check_ports(ctx)
    check_network(ctx)
    log_selinux(ctx)
