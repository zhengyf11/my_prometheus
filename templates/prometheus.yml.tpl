# ${managed_marker}
global:
  scrape_interval: ${scrape_interval}
  evaluation_interval: ${evaluation_interval}

rule_files:
  - "${rules_dir}/*.yml"
${alerting_config}
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:${prometheus_port}

  - job_name: node_exporter
    static_configs:
      - targets:
          - localhost:${node_exporter_port}

  - job_name: file_sd_nodes
    file_sd_configs:
      - files:
          - "${targets_dir}/*.yml"
        refresh_interval: 30s
