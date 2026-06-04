import logging
import os
import shutil

from .command import run

try:
    import grp
    import pwd
except ImportError:
    grp = None
    pwd = None


LOG = logging.getLogger(__name__)


def user_exists(name):
    if pwd is None:
        raise RuntimeError("system user management requires a POSIX platform")
    try:
        pwd.getpwnam(name)
        return True
    except KeyError:
        return False


def group_exists(name):
    if grp is None:
        raise RuntimeError("system group management requires a POSIX platform")
    try:
        grp.getgrnam(name)
        return True
    except KeyError:
        return False


def ensure_system_user(ctx, name):
    if user_exists(name):
        LOG.info("user exists: %s", name)
        return
    cmd = ["useradd", "--system", "--no-create-home", "--shell", "/sbin/nologin", name]
    run(ctx, cmd)
    LOG.info("created user: %s", name)


def chown_path(ctx, path, user=None, group=None, recursive=False):
    if ctx.dry_run:
        LOG.info("[dry-run] chown %s:%s %s", user or "", group or "", path)
        return
    if recursive:
        run(ctx, ["chown", "-R", "{0}:{1}".format(user or "", group or ""), str(path)])
    else:
        shutil.chown(str(path), user=user, group=group)


def chmod(path, mode):
    os.chmod(str(path), mode)
