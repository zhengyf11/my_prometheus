#!/usr/bin/env python3
"""Install Prometheus, Node Exporter, Grafana, and optional Alertmanager."""

from my_prometheus.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
