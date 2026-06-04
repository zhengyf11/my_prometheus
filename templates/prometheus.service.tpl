[Unit]
Description=Prometheus
Documentation=https://prometheus.io/docs/
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
Restart=on-failure
ExecStart=${bin_dir}/prometheus \
  --config.file=${config_file} \
  --storage.tsdb.path=${data_dir} \
  --storage.tsdb.retention.time=${retention_time} \
  --web.listen-address=${listen_address}:${prometheus_port} \
  --web.enable-lifecycle
NoNewPrivileges=true
ProtectHome=true
ProtectSystem=full
ReadWritePaths=${data_dir}

[Install]
WantedBy=multi-user.target
