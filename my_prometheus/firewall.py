import logging

from .command import command_exists, run


LOG = logging.getLogger(__name__)


def configure_firewall(ctx):
    if not ctx.open_firewall:
        LOG.info("firewall update skipped")
        return
    ports = [ctx.prometheus_port, ctx.grafana_port]
    if ctx.with_alertmanager:
        ports.append(ctx.alertmanager_port)

    active = run(ctx, ["systemctl", "is-active", "firewalld"], check=False, capture=True)
    if (active.stdout or "").strip() == "active":
        if not command_exists("firewall-cmd"):
            raise RuntimeError("firewalld is active but firewall-cmd was not found")
        for port in ports:
            run(ctx, ["firewall-cmd", "--add-port={0}/tcp".format(port), "--permanent"])
        run(ctx, ["firewall-cmd", "--reload"])
        LOG.info("firewall opened ports with firewalld: %s", ", ".join(str(p) for p in ports))
        return

    if command_exists("ufw"):
        status = run(ctx, ["ufw", "status"], check=False, capture=True)
        if (status.stdout or "").lower().startswith("status: active"):
            for port in ports:
                run(ctx, ["ufw", "allow", "{0}/tcp".format(port)])
            LOG.info("firewall opened ports with UFW: %s", ", ".join(str(p) for p in ports))
            return

    LOG.info("no active supported firewall; no firewall rules changed")
