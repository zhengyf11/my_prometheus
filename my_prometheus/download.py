import hashlib
import logging
import os
import shutil
import tarfile
import time
import urllib.request
import warnings
from pathlib import Path

from .files import ensure_dir


LOG = logging.getLogger(__name__)


def version_tag(version):
    return version if str(version).startswith("v") else "v" + str(version)


def version_number(version):
    value = str(version)
    return value[1:] if value.startswith("v") else value


def open_url(ctx, request, timeout):
    if isinstance(request, str):
        request = urllib.request.Request(request, headers={"User-Agent": "my_prometheus-installer"})
    if getattr(ctx, "proxy", None):
        proxy_handler = urllib.request.ProxyHandler({"http": ctx.proxy, "https": ctx.proxy})
        opener = urllib.request.build_opener(proxy_handler)
        return opener.open(request, timeout=timeout)
    return urllib.request.urlopen(request, timeout=timeout)


def fetch_url_bytes(ctx, url):
    attempts = max(1, int(ctx.download_retries))
    timeout = max(30, int(ctx.download_timeout))
    last_error = None
    for attempt in range(1, attempts + 1):
        LOG.info("fetching %s (attempt %s/%s)", url, attempt, attempts)
        try:
            with open_url(ctx, url, timeout) as response:
                return response.read()
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(10, attempt * 2))
    raise RuntimeError("failed to fetch {0}: {1}".format(url, last_error))


def download_file(ctx, url, dest, sha256=None):
    dest = Path(dest)
    ensure_dir(ctx, dest.parent)
    if dest.exists() and dest.stat().st_size > 0:
        temp = dest.with_name(dest.name + ".tmp")
        if temp.exists() and not ctx.dry_run:
            temp.unlink()
        verify_sha256(ctx, dest, sha256)
        LOG.info("using cached download: %s", dest)
        return dest
    if ctx.dry_run:
        LOG.info("[dry-run] download %s to %s", url, dest)
        return dest
    attempts = max(1, int(ctx.download_retries))
    timeout = max(30, int(ctx.download_timeout))
    temp = dest.with_name(dest.name + ".tmp")
    last_error = None
    for attempt in range(1, attempts + 1):
        LOG.info("downloading %s (attempt %s/%s)", url, attempt, attempts)
        req = urllib.request.Request(url, headers={"User-Agent": "my_prometheus-installer"})
        try:
            with open_url(ctx, req, timeout) as response:
                with open(str(temp), "wb") as handle:
                    shutil.copyfileobj(response, handle)
            verify_sha256(ctx, temp, sha256)
            os.replace(str(temp), str(dest))
            return dest
        except Exception as exc:
            last_error = exc
            if temp.exists():
                temp.unlink()
            if attempt < attempts:
                time.sleep(min(10, attempt * 2))
    raise RuntimeError(
        "failed to download {0} after {1} attempts: {2}. "
        "You can place the asset manually at {3} and rerun the installer.".format(
            url, attempts, last_error, dest
        )
    )


def load_checksum_map(ctx, project, version):
    if not ctx.verify_checksum:
        return {}
    if ctx.checksum_file:
        checksum_path = Path(ctx.checksum_file)
        if not checksum_path.exists():
            raise RuntimeError("checksum file does not exist: {0}".format(checksum_path))
        with open(str(checksum_path), "r") as handle:
            return parse_checksum_text(handle.read())
    url = github_release_tar_url(project, version, "sha256sums.txt")
    return parse_checksum_text(fetch_url_bytes(ctx, url).decode("utf-8", "replace"))


def release_asset_sha256(ctx, project, version, asset_name):
    if not ctx.verify_checksum:
        return None
    checksums = load_checksum_map(ctx, project, version)
    if asset_name not in checksums:
        raise RuntimeError("checksum for {0} was not found".format(asset_name))
    return checksums[asset_name]


def parse_checksum_text(text):
    checksums = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        digest = parts[0].strip()
        if not is_sha256_digest(digest):
            continue
        filename = parts[1].strip().lstrip("*")
        checksums[filename] = digest
    return checksums


def is_sha256_digest(value):
    if len(str(value)) != 64:
        return False
    try:
        int(str(value), 16)
    except ValueError:
        return False
    return True


def file_sha256(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(ctx, path, expected):
    if not ctx.verify_checksum or not expected:
        return
    if not is_sha256_digest(expected):
        raise RuntimeError("invalid sha256 checksum for {0}: {1}".format(path, expected))
    actual = file_sha256(path)
    if actual.lower() != expected.lower():
        raise RuntimeError(
            "checksum mismatch for {0}: expected {1}, got {2}".format(path, expected, actual)
        )
    LOG.info("verified checksum: %s", path)


def extract_tarball(ctx, tarball, dest_dir):
    tarball = Path(tarball)
    dest_dir = Path(dest_dir)
    ensure_dir(ctx, dest_dir)
    if ctx.dry_run:
        LOG.info("[dry-run] extract %s to %s", tarball, dest_dir)
        return dest_dir
    LOG.info("extracting %s", tarball)
    with tarfile.open(str(tarball), "r:gz") as archive:
        members = archive.getmembers()
        safe_members = []
        dest_root = dest_dir.resolve()
        for member in members:
            target = (dest_dir / member.name).resolve()
            if os.path.commonpath([str(dest_root), str(target)]) != str(dest_root):
                raise RuntimeError("unsafe path in tarball: {0}".format(member.name))
            safe_members.append(member)
        root_names = set(m.name.split("/")[0] for m in members if m.name)
        if len(root_names) == 1:
            existing = dest_dir / list(root_names)[0]
            if existing.exists():
                shutil.rmtree(str(existing))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            archive.extractall(str(dest_dir), members=safe_members)
    if len(root_names) == 1:
        return dest_dir / list(root_names)[0]
    return dest_dir


def github_release_tar_url(project, version, asset_name):
    tag = version_tag(version)
    return "https://github.com/prometheus/{0}/releases/download/{1}/{2}".format(
        project, tag, asset_name
    )


def install_binary(ctx, source, name):
    source = Path(source)
    dest = ctx.bin_dir / name
    ensure_dir(ctx, ctx.bin_dir)
    if ctx.dry_run:
        LOG.info("[dry-run] install binary %s to %s", source, dest)
        return
    changed = True
    if dest.exists():
        try:
            if source.read_bytes() == dest.read_bytes():
                changed = False
        except Exception:
            changed = True
    if changed:
        shutil.copy2(str(source), str(dest))
        LOG.info("installed binary %s", dest)
    else:
        LOG.info("binary already current: %s", dest)
    os.chmod(str(dest), 0o755)
