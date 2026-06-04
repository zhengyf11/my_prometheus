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


def download_file(ctx, url, dest):
    dest = Path(dest)
    ensure_dir(ctx, dest.parent)
    if dest.exists() and dest.stat().st_size > 0:
        temp = dest.with_name(dest.name + ".tmp")
        if temp.exists() and not ctx.dry_run:
            temp.unlink()
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
            with urllib.request.urlopen(req, timeout=timeout) as response:
                with open(str(temp), "wb") as handle:
                    shutil.copyfileobj(response, handle)
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
