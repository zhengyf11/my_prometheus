# ${managed_marker}
groups:
  - name: my_prometheus.rules
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "A scrape target is down"
          description: "Prometheus has not been able to scrape a configured target for more than 2 minutes."

      - alert: HostDiskAlmostFull
        expr: (1 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay|squashfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay|squashfs"}) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Host disk usage is above 90 percent"
