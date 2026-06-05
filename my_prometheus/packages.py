import logging
import gzip
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from .command import command_exists, run
from .download import download_file, fetch_url_bytes, version_number, verify_sha256
from .files import write_managed_file


LOG = logging.getLogger(__name__)


BASE_PACKAGES = ["tar", "gzip", "coreutils", "shadow-utils", "systemd", "openssl", "ca-certificates"]
GRAFANA_REPO_BASE = "https://rpm.grafana.com"


def install_packages(ctx, packages, extra_args=None):
    if not packages:
        return
    cmd = [ctx.package_manager, "-y"]
    if os.path.exists("/etc/yum.repos.d/grafana.repo"):
        cmd.append("--disablerepo=grafana")
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(["install"])
    cmd.extend(list(packages))
    run(ctx, cmd)


def ensure_base_packages(ctx):
    install_packages(ctx, BASE_PACKAGES)


def setup_grafana_repo(ctx):
    if command_exists("rpm"):
        run(
            ctx,
            [
                "rpm",
                "--import",
                "https://rpm.grafana.com/gpg.key",
            ],
            check=False,
        )

    repo = """[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=0
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
"""
    write_managed_file(ctx, "/etc/yum.repos.d/grafana.repo", repo, mode=0o644)


def install_grafana_package(ctx):
    was_installed = is_grafana_installed(ctx)
    setup_grafana_repo(ctx)
    rpm_path = resolve_grafana_rpm(ctx)
    install_packages(ctx, [str(rpm_path)])
    return was_installed


def is_grafana_installed(ctx):
    proc = run(ctx, ["rpm", "-q", "grafana"], check=False, capture=True)
    return proc.returncode == 0


def urlopen_bytes(ctx, url):
    return fetch_url_bytes(ctx, url)


def resolve_grafana_rpm(ctx):
    packages = load_grafana_packages(ctx)
    selected = select_grafana_package(ctx, packages)
    cached = find_cached_grafana_rpm(ctx, selected)
    if cached is not None:
        verify_sha256(ctx, cached, selected.get("checksum"))
        return cached
    href = selected["href"]
    filename = os.path.basename(href)
    url = GRAFANA_REPO_BASE + "/" + href.lstrip("/")
    return download_file(ctx, url, ctx.download_dir / filename, sha256=selected.get("checksum"))


def find_cached_grafana_rpm(ctx, selected=None):
    download_dir = Path(ctx.download_dir)
    if not download_dir.exists():
        return None
    requested = normalize_grafana_version(ctx.grafana_version)
    arch_tokens = [ctx.arch]
    if getattr(ctx, "prometheus_arch", None):
        arch_tokens.append(ctx.prometheus_arch)
    candidates = []
    selected_name = os.path.basename(selected["href"]) if selected else None
    for path in download_dir.glob("grafana-*.rpm"):
        name = path.name
        if selected_name and name != selected_name:
            continue
        if not any(token and token in name for token in arch_tokens):
            continue
        if requested != "latest" and "grafana-{0}-".format(requested) not in name:
            continue
        candidates.append(path)
    for path in download_dir.glob("grafana_*.rpm"):
        name = path.name
        if selected_name and name != selected_name:
            continue
        if not any(token and token in name for token in arch_tokens):
            continue
        if requested != "latest" and "grafana_{0}_".format(requested) not in name:
            continue
        candidates.append(path)
    if not candidates:
        return None
    selected = sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)[0]
    LOG.info("using cached Grafana RPM: %s", selected)
    return selected


def load_grafana_packages(ctx):
    repomd_url = GRAFANA_REPO_BASE + "/repodata/repomd.xml"
    repomd = ET.fromstring(urlopen_bytes(ctx, repomd_url))
    repo_ns = {"repo": "http://linux.duke.edu/metadata/repo"}
    primary_href = None
    for data in repomd.findall("repo:data", repo_ns):
        if data.get("type") == "primary":
            location = data.find("repo:location", repo_ns)
            if location is not None:
                primary_href = location.get("href")
                break
    if not primary_href:
        raise RuntimeError("Grafana repo primary metadata was not found")

    primary_url = GRAFANA_REPO_BASE + "/" + primary_href.lstrip("/")
    primary_gz = urlopen_bytes(ctx, primary_url)
    primary = gzip.decompress(primary_gz)
    root = ET.fromstring(primary)
    ns = {
        "common": "http://linux.duke.edu/metadata/common",
        "rpm": "http://linux.duke.edu/metadata/rpm",
    }
    packages = []
    for package in root.findall("common:package", ns):
        name = text_of(package.find("common:name", ns))
        arch = text_of(package.find("common:arch", ns))
        if name != "grafana" or arch != ctx.arch:
            continue
        version = package.find("common:version", ns)
        location = package.find("common:location", ns)
        time_node = package.find("common:time", ns)
        checksum_node = package.find("common:checksum", ns)
        if version is None or location is None:
            continue
        packages.append(
            {
                "version": version.get("ver"),
                "release": version.get("rel"),
                "epoch": version.get("epoch") or "0",
                "href": location.get("href"),
                "time": int(time_node.get("file", "0")) if time_node is not None else 0,
                "checksum": text_of(checksum_node),
                "checksum_type": checksum_node.get("type") if checksum_node is not None else None,
            }
        )
    if not packages:
        raise RuntimeError("no Grafana RPM package found for architecture {0}".format(ctx.arch))
    return packages


def text_of(node):
    return node.text if node is not None else None


def normalize_grafana_version(value):
    if not value:
        return "latest"
    value = version_number(value)
    return value.strip()


def select_grafana_package(ctx, packages):
    requested = normalize_grafana_version(ctx.grafana_version)
    if requested != "latest":
        for package in packages:
            full = "{0}-{1}".format(package["version"], package["release"])
            if requested in (package["version"], full):
                ensure_supported_checksum(ctx, package)
                LOG.info("selected Grafana RPM: %s-%s", package["version"], package["release"])
                return package
        raise RuntimeError("Grafana version {0} was not found in {1}".format(requested, GRAFANA_REPO_BASE))
    selected = sorted(packages, key=lambda item: item["time"], reverse=True)[0]
    ensure_supported_checksum(ctx, selected)
    LOG.info("selected latest Grafana RPM: %s-%s", selected["version"], selected["release"])
    return selected


def ensure_supported_checksum(ctx, package):
    if not ctx.verify_checksum:
        return
    if not package.get("checksum"):
        raise RuntimeError("Grafana package checksum was not found in repo metadata")
    if package.get("checksum_type") != "sha256":
        raise RuntimeError("unsupported Grafana checksum type: {0}".format(package.get("checksum_type")))
