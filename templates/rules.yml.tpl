# ${managed_marker}
groups:
  - name: sglang.recording
    interval: 30s
    rules:
      - record: my_prometheus:sglang_request_rate:5m
        expr: sum by (role, instance, model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m]))

      - record: my_prometheus:sglang_prompt_token_rate:5m
        expr: sum by (role, instance, model_name) (rate(sglang:prompt_tokens_total{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m]))

      - record: my_prometheus:sglang_generation_token_rate:5m
        expr: sum by (role, instance, model_name) (rate(sglang:generation_tokens_total{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m]))

      - record: my_prometheus:sglang_ttft_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, model_name, le) (rate(sglang:time_to_first_token_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_ttft_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, model_name, le) (rate(sglang:time_to_first_token_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_ttft_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:time_to_first_token_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_itl_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, model_name, le) (rate(sglang:inter_token_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_itl_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, model_name, le) (rate(sglang:inter_token_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_itl_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:inter_token_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_e2e_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, model_name, le) (rate(sglang:e2e_request_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_e2e_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, model_name, le) (rate(sglang:e2e_request_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_e2e_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:e2e_request_latency_seconds_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_kv_transfer_latency_ms_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_latency_ms_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_kv_transfer_latency_ms_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_latency_ms_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_kv_transfer_latency_ms_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_latency_ms_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_router_http_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, le) (rate(smg_http_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_http_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, le) (rate(smg_http_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_http_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, le) (rate(smg_http_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_request_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, le) (rate(smg_router_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_request_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, le) (rate(smg_router_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_request_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, le) (rate(smg_router_request_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_ttft_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, le) (rate(smg_router_ttft_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_ttft_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, le) (rate(smg_router_ttft_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_ttft_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, le) (rate(smg_router_ttft_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_tpot_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, le) (rate(smg_router_tpot_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_tpot_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, le) (rate(smg_router_tpot_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_tpot_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, le) (rate(smg_router_tpot_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_generation_seconds_p50:5m
        expr: histogram_quantile(0.50, sum by (role, instance, le) (rate(smg_router_generation_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_generation_seconds_p95:5m
        expr: histogram_quantile(0.95, sum by (role, instance, le) (rate(smg_router_generation_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_router_generation_seconds_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, le) (rate(smg_router_generation_duration_seconds_bucket{job="file_sd_nodes",role="sglang-router"}[5m])))

      - record: my_prometheus:sglang_kv_transfer_speed_gb_s_p99:5m
        expr: histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_speed_gb_s_bucket{job="file_sd_nodes",role=~"sglang-unified|sglang-prefill|sglang-decode"}[5m])))

      - record: my_prometheus:sglang_kv_transfer_failure_ratio:5m
        expr: sum by (role, instance, model_name) (rate(sglang:num_transfer_failed_reqs_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])), 1e-9)

      - record: my_prometheus:sglang_bootstrap_failure_ratio:5m
        expr: sum by (role, instance, model_name) (rate(sglang:num_bootstrap_failed_reqs_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])), 1e-9)

      - record: my_prometheus:sglang_prefill_retry_ratio:5m
        expr: sum by (role, instance, model_name) (rate(sglang:num_prefill_retries_total{job="file_sd_nodes",role="sglang-prefill"}[5m])) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role="sglang-prefill"}[5m])), 1e-9)

      - record: my_prometheus:sglang_prefill_decode_throughput_ratio:5m
        expr: sum by (model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role="sglang-prefill"}[5m])) / clamp_min(sum by (model_name) (rate(sglang:num_requests_total{job="file_sd_nodes",role="sglang-decode"}[5m])), 1e-9)

      - record: my_prometheus:sglang_prefill_decode_worker_capacity_ratio
        expr: sum by (role, instance, model) (smg_worker_pool_size{job="file_sd_nodes",role="sglang-router",worker_type="prefill"}) / clamp_min(sum by (role, instance, model) (smg_worker_pool_size{job="file_sd_nodes",role="sglang-router",worker_type="decode"}), 1)

      - record: my_prometheus:sglang_router_error_ratio:5m
        expr: sum by (role, instance) (rate(smg_router_request_errors_total{job="file_sd_nodes",role="sglang-router"}[5m])) / clamp_min(sum by (role, instance) (rate(smg_router_requests_total{job="file_sd_nodes",role="sglang-router"}[5m])), 1e-9)

      - record: my_prometheus:sglang_router_retry_exhausted_ratio:5m
        expr: sum by (role, instance) (rate(smg_worker_retries_exhausted_total{job="file_sd_nodes",role="sglang-router"}[5m])) / clamp_min(sum by (role, instance) (rate(smg_router_requests_total{job="file_sd_nodes",role="sglang-router"}[5m])), 1e-9)

      - record: my_prometheus:sglang_router_healthy_workers
        expr: sum by (role, instance) (smg_worker_health{job="file_sd_nodes",role="sglang-router"})

      - record: my_prometheus:sglang_router_open_circuit_breakers
        expr: sum by (role, instance) (smg_worker_cb_state{job="file_sd_nodes",role="sglang-router"} == bool 1)

      - record: my_prometheus:sglang_router_worker_load_skew
        expr: max by (role, instance) (smg_worker_requests_active{job="file_sd_nodes",role="sglang-router"}) / clamp_min(avg by (role, instance) (smg_worker_requests_active{job="file_sd_nodes",role="sglang-router"}), 1e-9)

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

      - alert: SGLangNoHealthyRouterWorkers
        expr: (my_prometheus:sglang_router_healthy_workers < 1) and on (instance) (max by (instance) (up{job="file_sd_nodes",role="sglang-router"}) == 1)
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "SGLang Router has no healthy workers"
          description: "The Router target is UP, but it has reported zero healthy backend workers for more than 2 minutes."

      - alert: SGLangKVTransferFailure
        expr: sum by (role, instance, model_name) (increase(sglang:num_transfer_failed_reqs_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "SGLang KV transfer failed"
          description: "At least one KV Cache transfer failed in the last 5 minutes."

      - alert: SGLangBootstrapFailure
        expr: sum by (role, instance, model_name) (increase(sglang:num_bootstrap_failed_reqs_total{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode"}[5m])) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "SGLang disaggregation bootstrap failed"
          description: "At least one PD bootstrap operation failed in the last 5 minutes."

      - alert: SGLangRouterRetryExhausted
        expr: sum by (role, instance) (increase(smg_worker_retries_exhausted_total{job="file_sd_nodes",role="sglang-router"}[5m])) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "SGLang Router exhausted backend retries"
          description: "At least one Router request exhausted all backend retries in the last 5 minutes."

      - alert: SGLangWorkerCircuitBreakerOpen
        expr: max by (role, instance, worker) (smg_worker_cb_state{job="file_sd_nodes",role="sglang-router"}) == 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "SGLang worker circuit breaker is open"
          description: "A Router backend worker circuit breaker has remained open for more than 2 minutes."

      - alert: SGLangRouterMeshDisconnected
        expr: router_mesh_peer_connections{job="file_sd_nodes",role="sglang-router"} == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "SGLang Router Mesh has no peer connections"
          description: "A Router Mesh instance has reported zero peer connections for more than 5 minutes."
