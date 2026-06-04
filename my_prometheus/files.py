import filecmp
import logging
import os
import shutil
import time
from pathlib import Path
from string import Template


LOG = logging.getLogger(__name__)

MANAGED_MARKER = "Managed by my_prometheus install.py"


def ensure_dir(ctx, path, mode=0o755, owner=None, group=None):
    path = Path(path)
    if ctx.dry_run:
        LOG.info("[dry-run] ensure directory %s", path)
        return
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(str(path), mode)
    if owner or group:
        shutil.chown(str(path), user=owner, group=group)


def read_text(path):
    with open(str(path), "r") as handle:
        return handle.read()


def write_text_atomic(path, content, mode=0o644):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with open(str(temp), "w") as handle:
        handle.write(content)
    os.chmod(str(temp), mode)
    os.replace(str(temp), str(path))


def backup_file(path):
    path = Path(path)
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup = path.with_name(path.name + ".bak." + timestamp)
    shutil.copy2(str(path), str(backup))
    return backup


def write_managed_file(ctx, path, content, mode=0o644, owner=None, group=None, marker=True):
    path = Path(path)
    if marker and MANAGED_MARKER not in content:
        if content.startswith("#!"):
            first, rest = content.split("\n", 1)
            content = first + "\n# " + MANAGED_MARKER + "\n" + rest
        else:
            content = "# " + MANAGED_MARKER + "\n" + content

    if ctx.dry_run:
        LOG.info("[dry-run] write %s", path)
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    changed = True
    if path.exists():
        old = read_text(path)
        if old == content:
            changed = False
        else:
            backup = backup_file(path)
            LOG.info("backed up %s to %s", path, backup)
    if changed:
        write_text_atomic(path, content, mode)
        LOG.info("wrote %s", path)
    os.chmod(str(path), mode)
    if owner or group:
        shutil.chown(str(path), user=owner, group=group)
    return changed


def render_template(ctx, name, values):
    template_path = ctx.templates_dir / name
    content = read_text(template_path)
    values = dict(values)
    values.setdefault("managed_marker", MANAGED_MARKER)
    return Template(content).safe_substitute(values)


def copy_file(ctx, source, dest, mode=0o644, owner=None, group=None):
    source = Path(source)
    dest = Path(dest)
    if ctx.dry_run:
        LOG.info("[dry-run] copy %s to %s", source, dest)
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    changed = True
    if dest.exists() and filecmp.cmp(str(source), str(dest), shallow=False):
        changed = False
    elif dest.exists():
        backup = backup_file(dest)
        LOG.info("backed up %s to %s", dest, backup)
    if changed:
        shutil.copy2(str(source), str(dest))
        LOG.info("copied %s to %s", source, dest)
    os.chmod(str(dest), mode)
    if owner or group:
        shutil.chown(str(dest), user=owner, group=group)
    return changed
