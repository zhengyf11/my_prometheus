import logging
import os
import shutil
import subprocess


LOG = logging.getLogger(__name__)


class CommandError(RuntimeError):
    def __init__(self, cmd, returncode, stdout="", stderr=""):
        self.cmd = [str(item) for item in cmd]
        self.returncode = returncode
        self.stdout = stdout or ""
        self.stderr = stderr or ""
        message = "command failed ({0}): {1}".format(returncode, " ".join(self.cmd))
        if self.stderr:
            message += "\n" + self.stderr.strip()
        super(CommandError, self).__init__(message)


def command_exists(name):
    return shutil.which(name) is not None


def redact_command(cmd, secrets=None):
    secrets = [s for s in (secrets or []) if s]
    safe = []
    for item in cmd:
        value = str(item)
        for secret in secrets:
            value = value.replace(secret, "******")
        safe.append(value)
    return safe


def run(ctx, cmd, check=True, capture=False, input_text=None, secrets=None, timeout=None):
    cmd = [str(item) for item in cmd]
    safe_cmd = redact_command(cmd, secrets)
    LOG.debug("run: %s", " ".join(safe_cmd))
    if ctx.dry_run:
        LOG.info("[dry-run] %s", " ".join(safe_cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    stdout = subprocess.PIPE if capture else None
    stderr = subprocess.PIPE if capture else None
    stdin = subprocess.PIPE if input_text is not None else None
    try:
        proc = subprocess.run(
            cmd,
            shell=False,
            check=False,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            universal_newlines=True,
            input=input_text,
            env=os.environ.copy(),
            timeout=timeout if timeout is not None else ctx.command_timeout,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("command timed out: {0}".format(" ".join(safe_cmd)))
    if check and proc.returncode != 0:
        raise CommandError(cmd, proc.returncode, proc.stdout, proc.stderr)
    return proc


def run_output(ctx, cmd, check=True):
    proc = run(ctx, cmd, check=check, capture=True)
    return (proc.stdout or "").strip()
