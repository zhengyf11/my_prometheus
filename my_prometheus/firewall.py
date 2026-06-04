import logging

from .command import command_exists, run


LOG = logging.getLogger(__name__)


def configure_firewall(ctx):
    if not ctx.open_firewall:
        LOG.info("firewall update skipped")
        return
    active = run(ctx, ["systemctl", "is-active", "firewalld"], check=False, capture=True)
    if (active.stdout or "").strip() != "active":
        LOG.info("firewalld is not active; no firewall rules changed")
        return
    if not command_exists("firewall-cmd"):
        LOG.info("firewalld is active but firewall-cmd was not found")
        return

    ports = [ctx.prometheus_port, ctx.grafana_port]
    if ctx.with_alertmanager:
        ports.append(ctx.alertmanager_port)
    for port in ports:
        run(ctx, ["firewall-cmd", "--add-port={0}/tcp".format(port), "--permanent"])
    run(ctx, ["firewall-cmd", "--reload"])
    LOG.info("firewall opened ports: %s", ", ".join(str(p) for p in ports))
