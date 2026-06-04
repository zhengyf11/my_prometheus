[Unit]
Description=Prometheus Alertmanager
Documentation=https://prometheus.io/docs/alerting/latest/alertmanager/
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
Restart=on-failure
ExecStart=${bin_dir}/alertmanager \
  --config.file=${config_file} \
  --storage.path=${data_dir} \
  --web.listen-address=${listen_address}:${alertmanager_port}
NoNewPrivileges=true
ProtectHome=true
ProtectSystem=full
ReadWritePaths=${data_dir}

[Install]
WantedBy=multi-user.target
