#!/usr/bin/env python3
"""Generate the complete SGLang Grafana dashboards from metric catalogs."""

import json
from collections import OrderedDict
from pathlib import Path

from sglang_translation_catalog import bilingual, load_catalog, validate_catalog as validate_translations


DATASOURCE_UID = "Prometheus"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "grafana" / "dashboards"
TRANSLATIONS = load_catalog()


def metric(name, metric_type):
    return {"name": name, "type": metric_type}


ENGINE_GROUPS = OrderedDict([
    ("HTTP, Process and Functions", [
        metric("sglang:http_requests_total", "counter"),
        metric("sglang:http_responses_total", "counter"),
        metric("sglang:http_requests_active", "gauge"),
        metric("sglang:routing_keys_active", "gauge"),
        metric("sglang:process_cpu_seconds_total", "counter"),
        metric("sglang:func_latency_seconds", "histogram"),
    ]),
    ("Requests, Tokens and User Latency", [
        metric("sglang:prompt_tokens_total", "counter"),
        metric("sglang:generation_tokens_total", "counter"),
        metric("sglang:spec_verify_calls_total", "counter"),
        metric("sglang:prompt_tokens_histogram", "histogram"),
        metric("sglang:uncached_prompt_tokens_histogram", "histogram"),
        metric("sglang:generation_tokens_histogram", "histogram"),
        metric("sglang:cached_tokens_total", "counter"),
        metric("sglang:num_requests_total", "counter"),
        metric("sglang:get_loads_duration_seconds", "histogram"),
        metric("sglang:num_so_requests_total", "counter"),
        metric("sglang:num_aborted_requests_total", "counter"),
        metric("sglang:time_to_first_token_seconds", "histogram"),
        metric("sglang:inter_token_latency_seconds", "histogram"),
        metric("sglang:e2e_request_latency_seconds", "histogram"),
    ]),
    ("Scheduler State", [
        metric("sglang:num_running_reqs", "gauge"),
        metric("sglang:num_queue_reqs", "gauge"),
        metric("sglang:num_grammar_queue_reqs", "gauge"),
        metric("sglang:gen_throughput", "gauge"),
        metric("sglang:cache_hit_rate", "gauge"),
        metric("sglang:decode_sum_seq_lens", "gauge"),
        metric("sglang:utilization", "gauge"),
        metric("sglang:fwd_occupancy", "gauge"),
        metric("sglang:new_token_ratio", "gauge"),
        metric("sglang:is_cuda_graph", "gauge"),
    ]),
    ("KV, SWA and Mamba Pools", [
        metric("sglang:token_usage", "gauge"),
        metric("sglang:full_token_usage", "gauge"),
        metric("sglang:swa_token_usage", "gauge"),
        metric("sglang:mamba_usage", "gauge"),
        metric("sglang:num_used_tokens", "gauge"),
        metric("sglang:kv_available_tokens", "gauge"),
        metric("sglang:kv_evictable_tokens", "gauge"),
        metric("sglang:kv_used_tokens", "gauge"),
        metric("sglang:swa_available_tokens", "gauge"),
        metric("sglang:swa_evictable_tokens", "gauge"),
        metric("sglang:swa_used_tokens", "gauge"),
        metric("sglang:mamba_available_tokens", "gauge"),
        metric("sglang:mamba_evictable_tokens", "gauge"),
        metric("sglang:mamba_used_tokens", "gauge"),
    ]),
    ("CUDA, Tokens and MFU Runtime", [
        metric("sglang:cuda_graph_passes_total", "counter"),
        metric("sglang:realtime_tokens_total", "counter"),
        metric("sglang:forward_execution_seconds_total", "counter"),
        metric("sglang:estimated_flops_per_gpu_total", "counter"),
        metric("sglang:estimated_read_bytes_per_gpu_total", "counter"),
        metric("sglang:estimated_write_bytes_per_gpu_total", "counter"),
        metric("sglang:dp_cooperation_realtime_tokens_total", "counter"),
        metric("sglang:dp_cooperation_forward_execution_seconds_total", "counter"),
    ]),
    ("Engine Capacity and Startup", [
        metric("sglang:max_total_num_tokens", "gauge"),
        metric("sglang:max_running_requests_under_SLO", "gauge"),
        metric("sglang:engine_startup_time", "gauge"),
        metric("sglang:engine_load_weights_time", "gauge"),
        metric("sglang:page_size", "gauge"),
        metric("sglang:num_pages", "gauge"),
        metric("sglang:context_len", "gauge"),
        metric("sglang:startup_available_gpu_memory_gb", "gauge"),
        metric("sglang:weight_load_duration_seconds", "gauge"),
    ]),
    ("Retraction, Queue and Stage Latency", [
        metric("sglang:num_retracted_reqs", "gauge"),
        metric("sglang:num_retracted_requests_total", "counter"),
        metric("sglang:num_retracted_input_tokens_total", "counter"),
        metric("sglang:num_retracted_output_tokens_total", "counter"),
        metric("sglang:num_paused_reqs", "gauge"),
        metric("sglang:queue_time_seconds", "histogram"),
        metric("sglang:per_stage_req_latency_seconds", "histogram"),
    ]),
    ("Grammar", [
        metric("sglang:grammar_compilation_time_seconds", "histogram"),
        metric("sglang:num_grammar_cache_hit_total", "counter"),
        metric("sglang:num_grammar_aborted_total", "counter"),
        metric("sglang:num_grammar_timeout_total", "counter"),
        metric("sglang:num_grammar_total", "counter"),
        metric("sglang:grammar_schema_count", "histogram"),
        metric("sglang:grammar_ebnf_size", "histogram"),
        metric("sglang:grammar_tree_traversal_time_avg", "histogram"),
        metric("sglang:grammar_tree_traversal_time_max", "histogram"),
    ]),
    ("Speculative Decoding and Prefill Delayer", [
        metric("sglang:spec_accept_length", "gauge"),
        metric("sglang:spec_accept_rate", "gauge"),
        metric("sglang:spec_cap_length", "gauge"),
        metric("sglang:spec_block_accept_length", "gauge"),
        metric("sglang:spec_num_steps", "gauge"),
        metric("sglang:spec_num_draft_tokens", "gauge"),
        metric("sglang:prefill_delayer_wait_forward_passes", "histogram"),
        metric("sglang:prefill_delayer_wait_seconds", "histogram"),
        metric("sglang:prefill_delayer_outcomes_total", "counter"),
    ]),
    ("PD Queues and KV Transfer", [
        metric("sglang:num_prefill_bootstrap_queue_reqs", "gauge"),
        metric("sglang:num_prefill_inflight_queue_reqs", "gauge"),
        metric("sglang:num_decode_prealloc_queue_reqs", "gauge"),
        metric("sglang:num_decode_transfer_queue_reqs", "gauge"),
        metric("sglang:pending_prealloc_token_usage", "gauge"),
        metric("sglang:kv_transfer_speed_gb_s", "histogram"),
        metric("sglang:kv_transfer_latency_ms", "histogram"),
        metric("sglang:kv_transfer_total_mb", "histogram"),
        metric("sglang:kv_transfer_bootstrap_ms", "histogram"),
        metric("sglang:kv_transfer_alloc_ms", "histogram"),
        metric("sglang:num_bootstrap_failed_reqs_total", "counter"),
        metric("sglang:num_transfer_failed_reqs_total", "counter"),
        metric("sglang:num_prefill_retries_total", "counter"),
    ]),
    ("Prefix Cache and Routing Keys", [
        metric("sglang:eviction_duration_seconds", "histogram"),
        metric("sglang:evicted_tokens_total", "counter"),
        metric("sglang:load_back_duration_seconds", "histogram"),
        metric("sglang:load_back_tokens_total", "counter"),
        metric("sglang:num_unique_running_routing_keys", "gauge"),
        metric("sglang:routing_key_running_req_count", "gauge"),
        metric("sglang:routing_key_all_req_count", "gauge"),
    ]),
    ("Optional LoRA, HiCache, Streaming and EPLB", [
        metric("sglang:lora_pool_slots_used", "gauge"),
        metric("sglang:lora_pool_slots_total", "gauge"),
        metric("sglang:lora_pool_utilization", "gauge"),
        metric("sglang:hicache_host_used_tokens", "gauge"),
        metric("sglang:hicache_host_total_tokens", "gauge"),
        metric("sglang:num_streaming_sessions", "gauge"),
        metric("sglang:streaming_session_held_tokens", "gauge"),
        metric("sglang:prefetched_tokens_total", "counter"),
        metric("sglang:backuped_tokens_total", "counter"),
        metric("sglang:prefetch_pgs", "histogram"),
        metric("sglang:backup_pgs", "histogram"),
        metric("sglang:prefetch_bandwidth", "histogram"),
        metric("sglang:backup_bandwidth", "histogram"),
        metric("sglang:eplb_gpu_physical_count", "histogram"),
        metric("sglang:eplb_balancedness", "summary"),
        metric("sglang:failed_session_recoveries_total", "counter"),
    ]),
])


ROUTER_GROUPS = OrderedDict([
    ("HTTP and Router Requests", [
        metric("smg_http_requests_total", "counter"),
        metric("smg_http_request_duration_seconds", "histogram"),
        metric("smg_http_inflight_request_age_count", "gauge"),
        metric("smg_http_responses_total", "counter"),
        metric("smg_http_connections_active", "gauge"),
        metric("smg_http_rate_limit_total", "counter"),
        metric("smg_router_requests_total", "counter"),
        metric("smg_router_request_duration_seconds", "histogram"),
        metric("smg_router_request_errors_total", "counter"),
        metric("smg_router_stage_duration_seconds", "histogram"),
        metric("smg_router_upstream_responses_total", "counter"),
        metric("smg_router_ttft_seconds", "histogram"),
        metric("smg_router_tpot_seconds", "histogram"),
        metric("smg_router_tokens_total", "counter"),
        metric("smg_router_generation_duration_seconds", "histogram"),
    ]),
    ("Worker Pool and Health", [
        metric("smg_worker_pool_size", "gauge"),
        metric("smg_worker_connections_active", "gauge"),
        metric("smg_worker_requests_active", "gauge"),
        metric("smg_worker_health", "gauge"),
        metric("smg_worker_health_checks_total", "counter"),
        metric("smg_worker_selection_total", "counter"),
        metric("smg_worker_errors_total", "counter"),
        metric("smg_worker_routing_keys_active", "gauge"),
    ]),
    ("Policies, Circuit Breaker and Retries", [
        metric("smg_manual_policy_cache_entries", "gauge"),
        metric("smg_manual_policy_branch_total", "counter"),
        metric("smg_consistent_hashing_policy_branch_total", "counter"),
        metric("smg_prefix_hash_policy_branch_total", "counter"),
        metric("smg_worker_cb_state", "gauge"),
        metric("smg_worker_cb_transitions_total", "counter"),
        metric("smg_worker_cb_outcomes_total", "counter"),
        metric("smg_worker_cb_consecutive_failures", "gauge"),
        metric("smg_worker_cb_consecutive_successes", "gauge"),
        metric("smg_worker_retries_total", "counter"),
        metric("smg_worker_retries_exhausted_total", "counter"),
        metric("smg_worker_retry_backoff_seconds", "histogram"),
    ]),
    ("Discovery, MCP and Persistence", [
        metric("smg_discovery_registrations_total", "counter"),
        metric("smg_discovery_deregistrations_total", "counter"),
        metric("smg_discovery_sync_duration_seconds", "histogram"),
        metric("smg_discovery_workers_discovered", "gauge"),
        metric("smg_mcp_tool_calls_total", "counter"),
        metric("smg_mcp_tool_duration_seconds", "histogram"),
        metric("smg_mcp_servers_active", "gauge"),
        metric("smg_mcp_tool_iterations_total", "counter"),
        metric("smg_db_operations_total", "counter"),
        metric("smg_db_operation_duration_seconds", "histogram"),
        metric("smg_db_connections_active", "gauge"),
        metric("smg_db_items_stored", "counter"),
    ]),
    ("Router Mesh", [
        metric("router_mesh_convergence_ms", "histogram"),
        metric("router_mesh_batches_total", "counter"),
        metric("router_mesh_bytes_total", "counter"),
        metric("router_mesh_snapshot_trigger_total", "counter"),
        metric("router_mesh_snapshot_duration_seconds", "histogram"),
        metric("router_mesh_snapshot_bytes_total", "counter"),
        metric("router_mesh_peer_connections", "gauge"),
        metric("router_mesh_peer_reconnects_total", "counter"),
        metric("router_mesh_peer_ack_total", "counter"),
        metric("router_mesh_peer_nack_total", "counter"),
        metric("router_mesh_store_cardinality", "gauge"),
        metric("router_mesh_store_hash", "gauge"),
        metric("router_rl_drift_ratio", "gauge"),
        metric("router_lb_drift_ratio", "gauge"),
    ]),
])


KEY_ENGINE_METRICS = (
    "sglang:num_requests_total",
    "sglang:prompt_tokens_total",
    "sglang:generation_tokens_total",
    "sglang:num_aborted_requests_total",
    "sglang:num_running_reqs",
    "sglang:num_queue_reqs",
    "sglang:token_usage",
    "sglang:utilization",
    "sglang:time_to_first_token_seconds",
    "sglang:inter_token_latency_seconds",
    "sglang:e2e_request_latency_seconds",
    "sglang:kv_transfer_latency_ms",
    "sglang:num_transfer_failed_reqs_total",
    "sglang:num_bootstrap_failed_reqs_total",
    "sglang:num_prefill_retries_total",
)

ENGINE_LATENCY_METRICS = (
    "sglang:queue_time_seconds",
    "sglang:prefill_delayer_wait_seconds",
    "sglang:kv_transfer_bootstrap_ms",
    "sglang:kv_transfer_alloc_ms",
    "sglang:per_stage_req_latency_seconds",
)

KEY_ROUTER_METRICS = (
    "smg_http_requests_total",
    "smg_http_responses_total",
    "smg_http_rate_limit_total",
    "smg_http_connections_active",
    "smg_router_requests_total",
    "smg_router_request_errors_total",
    "smg_worker_pool_size",
    "smg_worker_requests_active",
    "smg_worker_health",
    "smg_worker_retries_total",
    "smg_worker_retries_exhausted_total",
    "smg_worker_cb_state",
)

ROUTER_LATENCY_METRICS = (
    "smg_http_request_duration_seconds",
    "smg_router_request_duration_seconds",
    "smg_router_stage_duration_seconds",
    "smg_router_ttft_seconds",
    "smg_router_tpot_seconds",
    "smg_router_generation_duration_seconds",
)

SLO_LATENCY_METRICS = {
    "sglang:time_to_first_token_seconds",
    "sglang:inter_token_latency_seconds",
    "sglang:e2e_request_latency_seconds",
    "sglang:kv_transfer_latency_ms",
    "smg_http_request_duration_seconds",
    "smg_router_request_duration_seconds",
    "smg_router_ttft_seconds",
    "smg_router_tpot_seconds",
    "smg_router_generation_duration_seconds",
}

RECORDED_LATENCY_PREFIXES = {
    "sglang:time_to_first_token_seconds": "my_prometheus:sglang_ttft_seconds",
    "sglang:inter_token_latency_seconds": "my_prometheus:sglang_itl_seconds",
    "sglang:e2e_request_latency_seconds": "my_prometheus:sglang_e2e_seconds",
    "sglang:kv_transfer_latency_ms": "my_prometheus:sglang_kv_transfer_latency_ms",
    "smg_http_request_duration_seconds": "my_prometheus:sglang_router_http_seconds",
    "smg_router_request_duration_seconds": "my_prometheus:sglang_router_request_seconds",
    "smg_router_ttft_seconds": "my_prometheus:sglang_router_ttft_seconds",
    "smg_router_tpot_seconds": "my_prometheus:sglang_router_tpot_seconds",
    "smg_router_generation_duration_seconds": "my_prometheus:sglang_router_generation_seconds",
}

STATIC_METRICS = {
    "sglang:max_total_num_tokens",
    "sglang:max_running_requests_under_SLO",
    "sglang:engine_startup_time",
    "sglang:engine_load_weights_time",
    "sglang:page_size",
    "sglang:num_pages",
    "sglang:context_len",
    "sglang:startup_available_gpu_memory_gb",
    "sglang:spec_num_steps",
    "sglang:spec_num_draft_tokens",
    "sglang:lora_pool_slots_total",
    "sglang:hicache_host_total_tokens",
}

PERCENT_METRICS = {
    "sglang:cache_hit_rate",
    "sglang:token_usage",
    "sglang:full_token_usage",
    "sglang:swa_token_usage",
    "sglang:mamba_usage",
    "sglang:utilization",
    "sglang:fwd_occupancy",
    "sglang:new_token_ratio",
    "sglang:lora_pool_utilization",
    "sglang:spec_accept_rate",
    "sglang:eplb_balancedness",
    "router_rl_drift_ratio",
    "router_lb_drift_ratio",
}

ENGINE_INSTANCE_METRICS = {
    "sglang:http_requests_total",
    "sglang:http_responses_total",
    "sglang:http_requests_active",
    "sglang:routing_keys_active",
    "sglang:process_cpu_seconds_total",
    "sglang:func_latency_seconds",
}

RATE_DISPLAY_OVERRIDES = {
    "sglang:num_requests_total": (
        "请求完成速率",
        "每秒完成的推理请求数",
    ),
    "sglang:prompt_tokens_total": (
        "Prefill 吞吐",
        "每秒处理的输入 Token 数",
    ),
    "sglang:generation_tokens_total": (
        "Decode 吞吐",
        "每秒生成的输出 Token 数",
    ),
    "smg_router_requests_total": (
        "客户请求速率",
        "Router 每秒接收的推理请求数",
    ),
    "sglang:process_cpu_seconds_total": (
        "进程 CPU 使用量",
        "进程每秒消耗的 CPU 秒数",
    ),
    "sglang:forward_execution_seconds_total": (
        "前向计算时间占比",
        "每秒累计的前向计算秒数",
    ),
    "sglang:dp_cooperation_forward_execution_seconds_total": (
        "DP 协同前向时间占比",
        "每秒累计的 DP 协同前向计算秒数",
    ),
    "sglang:estimated_flops_per_gpu_total": (
        "单 GPU 估算计算吞吐",
        "每个 GPU 每秒估算的浮点运算量",
    ),
    "sglang:estimated_read_bytes_per_gpu_total": (
        "单 GPU 估算显存读取带宽",
        "每个 GPU 每秒估算的显存读取字节数",
    ),
    "sglang:estimated_write_bytes_per_gpu_total": (
        "单 GPU 估算显存写入带宽",
        "每个 GPU 每秒估算的显存写入字节数",
    ),
}

SPLIT_ROLE_METRICS = {
    "sglang:prompt_tokens_total": "sglang-prefill",
    "sglang:prompt_tokens_histogram": "sglang-prefill",
    "sglang:uncached_prompt_tokens_histogram": "sglang-prefill",
    "sglang:generation_tokens_total": "sglang-decode",
    "sglang:generation_tokens_histogram": "sglang-decode",
    "sglang:num_prefill_retries_total": "sglang-prefill",
}

LAZY_COUNTER_BASELINES = {
    "sglang:num_aborted_requests_total": "sglang:num_requests_total",
    "sglang:num_transfer_failed_reqs_total": "sglang:num_requests_total",
    "sglang:num_bootstrap_failed_reqs_total": "sglang:num_requests_total",
    "sglang:num_prefill_retries_total": "sglang:num_requests_total",
    "smg_router_request_errors_total": "smg_router_requests_total",
    "smg_worker_retries_exhausted_total": "smg_router_requests_total",
}

INPUT_TOKEN_BUCKETS = (
    ("0-4k", None, ("4000", "4000[.]0")),
    ("4k-15k", ("4000", "4000[.]0"), ("15000", "15000[.]0")),
    ("15k-60k", ("15000", "15000[.]0"), ("60000", "60000[.]0")),
    ("60k-300k", ("60000", "60000[.]0"), ("300000", "300000[.]0")),
    (
        "300k-1M",
        ("300000", "300000[.]0"),
        ("1000000", "1000000[.]0", "1e[+]06"),
    ),
    ("1M+", ("1000000", "1000000[.]0", "1e[+]06"), None),
)

GENERATION_TOKEN_BUCKETS = (
    ("0-500", None, ("500", "500[.]0")),
    ("500-2k", ("500", "500[.]0"), ("2000", "2000[.]0")),
    ("2k-8k", ("2000", "2000[.]0"), ("8000", "8000[.]0")),
    ("8k-30k", ("8000", "8000[.]0"), ("30000", "30000[.]0")),
    ("30k-100k", ("30000", "30000[.]0"), ("100000", "100000[.]0")),
    ("100k+", ("100000", "100000[.]0"), None),
)


def prioritize_groups(groups, prioritized):
    """Move selected metrics into ordered overview groups without duplicating them."""
    lookup = {
        item["name"]: item
        for items in groups.values()
        for item in items
    }
    selected_names = set(name for _, names in prioritized for name in names)
    output = OrderedDict()
    for title, names in prioritized:
        output[title] = [lookup[name] for name in names]
    for title, items in groups.items():
        remaining = [item for item in items if item["name"] not in selected_names]
        if remaining:
            output[title] = remaining
    return output


ENGINE_GROUPS = prioritize_groups(
    ENGINE_GROUPS,
    (
        ("Key Engine Metrics", KEY_ENGINE_METRICS),
        ("Request Latency Pipeline", ENGINE_LATENCY_METRICS),
    ),
)

ROUTER_GROUPS = prioritize_groups(
    ROUTER_GROUPS,
    (
        ("Key Router Metrics", KEY_ROUTER_METRICS),
        ("Router Request Latency Pipeline", ROUTER_LATENCY_METRICS),
    ),
)


def flatten(groups):
    return [item for items in groups.values() for item in items]


def datasource():
    return {"type": "prometheus", "uid": DATASOURCE_UID}


def category_title(original):
    return bilingual(TRANSLATIONS["categories"][original], original)


def metric_translation(item):
    return TRANSLATIONS["metrics"][item["name"]]


def short_explanation(item):
    description = metric_translation(item)["description"].strip().rstrip("。")
    for separator in ("；", "，单位", "，按"):
        if separator in description:
            description = description.split(separator, 1)[0]
    return description


def rate_display(item):
    name = item["name"]
    if name in RATE_DISPLAY_OVERRIDES:
        return RATE_DISPLAY_OVERRIDES[name]
    title = metric_translation(item)["title"]
    replaced = False
    for suffix in ("总数", "总量"):
        if title.endswith(suffix):
            title = title[:-len(suffix)] + "速率"
            replaced = True
            break
    if not replaced and title.endswith("次数"):
        title = title[:-2] + "频率"
        replaced = True
    if not replaced:
        title += "速率"
    return title, "原始累计指标每秒增加的数量"


def metric_title(item):
    if item["type"] == "counter":
        title, _ = rate_display(item)
        return title
    return metric_translation(item)["title"]


def metric_mapping(item):
    translation = metric_translation(item)
    lines = [
        "- 中文名称：{0}".format(translation["title"]),
        "- Prometheus 原指标：`{0}`".format(item["name"]),
        "- 指标类型：`{0}`".format(item["type"]),
        "- 说明：{0}".format(translation["description"]),
    ]
    if item["type"] == "counter":
        lines.append("- 面板口径：使用 `rate()` 展示每秒速率，不是累计总数。")
    if metric_scope(item) == "engine-instance":
        lines.append("- 筛选口径：实例级指标，不受模型 (Model) 变量影响。")
    return "\n".join(lines)


def metric_unit(item):
    name = item["name"]
    metric_type = item["type"]
    if name in PERCENT_METRICS:
        return "percentunit"
    if name == "sglang:startup_available_gpu_memory_gb":
        return "suffix: GB"
    if name in ("sglang:kv_transfer_speed_gb_s", "sglang:prefetch_bandwidth", "sglang:backup_bandwidth"):
        return "suffix: GB/s"
    if name == "sglang:kv_transfer_total_mb":
        return "suffix: MB"
    if name == "sglang:gen_throughput":
        return "suffix: Token/s"
    if name == "sglang:estimated_flops_per_gpu_total":
        return "suffix: FLOP/s"
    if name in (
        "sglang:engine_startup_time",
        "sglang:engine_load_weights_time",
        "sglang:grammar_tree_traversal_time_avg",
        "sglang:grammar_tree_traversal_time_max",
    ):
        return "s"
    if name.endswith("_ms"):
        return "ms"
    if name.endswith("_seconds") or "_seconds_" in name:
        return "suffix: s/s" if metric_type == "counter" else "s"
    if metric_type == "counter":
        if "bytes" in name:
            return "Bps"
        if "token" in name:
            return "suffix: Token/s"
        return "ops"
    return "short"


def metric_scope(item):
    name = item["name"]
    if name.startswith(("smg_", "router_")):
        return "router-instance"
    if name in ENGINE_INSTANCE_METRICS:
        return "engine-instance"
    return "engine-model"


def selector(item, kind):
    labels = ['instance=~"$instance"']
    if kind == "unified":
        labels.append('role="sglang-unified"')
    elif kind == "split-router":
        labels.append('role=~"$role"')
        fixed_role = SPLIT_ROLE_METRICS.get(item["name"])
        if fixed_role:
            labels.append('role="{0}"'.format(fixed_role))
    if metric_scope(item) == "engine-model":
        labels.append('model_name=~"$model"')
    return ",".join(labels)


def aggregation_labels(item, include_le=False, include_quantile=False):
    labels = ["role", "instance"]
    if metric_scope(item) == "engine-model":
        labels.append("model_name")
    if include_le:
        labels.append("le")
    if include_quantile:
        labels.append("quantile")
    return ", ".join(labels)


def legend_format(item, suffix=None):
    labels = ["{{role}}", "{{instance}}"]
    if metric_scope(item) == "engine-model":
        labels.append("{{model_name}}")
    if suffix:
        labels.append(suffix)
    return " / ".join(labels)


def expression(item, kind):
    name = item["name"]
    metric_type = item["type"]
    labels = selector(item, kind)
    if metric_type == "counter":
        rate_expression = "sum by ({0}) (rate({1}{{{2}}}[$__rate_interval]))".format(
            aggregation_labels(item), name, labels
        )
        baseline = LAZY_COUNTER_BASELINES.get(name)
        if baseline:
            baseline_expression = "sum by ({0}) (rate({1}{{{2}}}[$__rate_interval])) * 0".format(
                aggregation_labels(item), baseline, labels
            )
            return "({0}) or ({1})".format(rate_expression, baseline_expression)
        return rate_expression
    if metric_type == "summary":
        return "max by ({0}) ({1}{{{2}}})".format(
            aggregation_labels(item, include_quantile=True), name, labels
        )
    return "max by ({0}) ({1}{{{2}}})".format(
        aggregation_labels(item), name, labels
    )


def histogram_quantile_expression(item, kind, quantile):
    return (
        "histogram_quantile({0}, sum by ({1}) "
        "(rate({2}_bucket{{{3}}}[$__rate_interval])))"
    ).format(
        quantile,
        aggregation_labels(item, include_le=True),
        item["name"],
        selector(item, kind),
    )


def recorded_latency_expression(item, kind, quantile):
    labels = ['instance=~"$instance"']
    if kind == "unified":
        labels.append('role="sglang-unified"')
    else:
        labels.append('role=~"$role"')
    if metric_scope(item) == "engine-model":
        labels.append('model_name=~"$model"')
    suffix = {"0.50": "p50", "0.95": "p95", "0.99": "p99"}[quantile]
    recorded = "{0}_{1}:5m{{{2}}}".format(
        RECORDED_LATENCY_PREFIXES[item["name"]], suffix, ",".join(labels)
    )
    raw = histogram_quantile_expression(item, kind, quantile)
    return "({0}) or ({1})".format(recorded, raw)


def histogram_mean_expression(item, kind):
    name = item["name"]
    labels = selector(item, kind)
    return (
        "sum by ({0}) (rate({1}_sum{{{2}}}[$__rate_interval])) / "
        "clamp_min(sum by ({0}) (rate({1}_count{{{2}}}[$__rate_interval])), 1e-9)"
    ).format(aggregation_labels(item), name, labels)


def cumulative_bucket_expression(item, kind, bounds):
    labels = selector(item, kind)
    if bounds is None:
        return "sum by ({0}) (increase({1}_count{{{2}}}[$__range]))".format(
            aggregation_labels(item), item["name"], labels
        )
    return (
        'sum by ({0}) (increase({1}_bucket{{{2},le=~"{3}"}}[$__range]))'
    ).format(aggregation_labels(item), item["name"], labels, "|".join(bounds))


def bucket_range_expression(item, kind, lower, upper):
    upper_expression = cumulative_bucket_expression(item, kind, upper)
    if lower is None:
        return "round({0})".format(upper_expression)
    lower_expression = cumulative_bucket_expression(item, kind, lower)
    return "round(clamp_min(({0}) - ({1}), 0))".format(
        upper_expression, lower_expression
    )


def cache_hit_expression(item, kind):
    labels = selector(item, kind)
    total = (
        "sum by ({0}) (rate(sglang:prompt_tokens_histogram_sum{{{1}}}"
        "[$__rate_interval]))"
    ).format(aggregation_labels(item), labels)
    uncached = (
        "sum by ({0}) (rate(sglang:uncached_prompt_tokens_histogram_sum{{{1}}}"
        "[$__rate_interval]))"
    ).format(aggregation_labels(item), labels)
    return "clamp_max(clamp_min(1 - ({0}) / clamp_min(({1}), 1e-9), 0), 1)".format(
        uncached, total
    )


def ref_id(index):
    return "Q{0:02d}".format(index + 1)


def target(expression_value, legend, index, instant=False):
    result = {
        "datasource": datasource(),
        "expr": expression_value,
        "legendFormat": legend,
        "refId": ref_id(index),
    }
    if instant:
        result["instant"] = True
    return result


def timeseries_options():
    return {
        "legend": {
            "calcs": ["lastNotNull", "max"],
            "displayMode": "table",
            "placement": "bottom",
            "showLegend": True,
        },
        "tooltip": {"mode": "multi", "sort": "desc"},
    }


def timeseries_custom_options():
    return {
        "drawStyle": "line",
        "fillOpacity": 10,
        "lineWidth": 1,
        "showPoints": "never",
        "spanNulls": False,
    }


def panel_base(item, panel_id, x, y, width, unit):
    defaults = {
        "color": {"mode": "palette-classic"},
        "min": 0,
        "unit": unit,
    }
    if unit == "percentunit":
        defaults["max"] = 1
    return {
        "datasource": datasource(),
        "description": metric_mapping(item),
        "fieldConfig": {
            "defaults": defaults,
            "overrides": [],
        },
        "gridPos": {"h": 8, "w": width, "x": x, "y": y},
        "id": panel_id,
        "targets": [],
        "title": metric_title(item),
    }


def token_distribution_panel(item, panel_id, x, y, width, kind, buckets):
    panel = panel_base(item, panel_id, x, y, width, "short")
    panel["description"] += (
        "\n- 统计口径：所选 Dashboard 时间范围内完成请求的分段数量。"
        "\n- 分段边界：使用 SGLang 当前默认 Histogram bucket，通过相邻累计值相减计算。"
    )
    panel["targets"] = [
        target(
            bucket_range_expression(item, kind, lower, upper),
            legend_format(item, label),
            index,
            instant=True,
        )
        for index, (label, lower, upper) in enumerate(buckets)
    ]
    panel["options"] = {
        "displayMode": "gradient",
        "minVizHeight": 10,
        "minVizWidth": 0,
        "orientation": "horizontal",
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
        "showUnfilled": True,
    }
    panel["type"] = "bargauge"
    return panel


def cache_hit_panel(item, panel_id, x, y, width, kind):
    panel = panel_base(item, panel_id, x, y, width, "percentunit")
    panel["title"] = "输入 Token 缓存命中率"
    panel["description"] = "\n".join([
        "- 计算公式：`1 - 未缓存输入 Token / 总输入 Token`。",
        "- 被替代的 Prometheus 原指标族：`sglang:uncached_prompt_tokens_histogram`",
        "- Prometheus 原指标：`sglang:prompt_tokens_histogram_sum`",
        "- Prometheus 原指标：`sglang:uncached_prompt_tokens_histogram_sum`",
        "- 原始未缓存输入 Token 长度分布不单独展示。",
    ])
    panel["fieldConfig"]["defaults"]["custom"] = timeseries_custom_options()
    panel["options"] = timeseries_options()
    panel["targets"] = [target(cache_hit_expression(item, kind), legend_format(item), 0)]
    panel["type"] = "timeseries"
    return panel


def router_response_ratio_expression(item, kind, status_pattern):
    labels = selector(item, kind)
    aggregation = aggregation_labels(item)
    total = "sum by ({0}) (rate({1}{{{2}}}[$__rate_interval]))".format(
        aggregation, item["name"], labels
    )
    matching = (
        'sum by ({0}) (rate({1}{{{2},status_code=~"{3}"}}[$__rate_interval]))'
    ).format(aggregation, item["name"], labels, status_pattern)
    numerator = "(({0}) or ({1} * 0))".format(matching, total)
    return "{0} / clamp_min(({1}), 1e-9)".format(numerator, total)


def router_response_outcome_panel(item, panel_id, x, y, width, kind):
    panel = panel_base(item, panel_id, x, y, width, "percentunit")
    panel["title"] = "Router HTTP 响应占比"
    panel["description"] = panel["description"].replace(
        "- 面板口径：使用 `rate()` 展示每秒速率，不是累计总数。",
        "- 面板口径：先用 `rate()` 计算各状态响应速率，再除以全部响应速率得到占比。",
    )
    panel["targets"] = [
        target(router_response_ratio_expression(item, kind, "2.."), legend_format(item, "成功 (2xx)"), 0),
        target(router_response_ratio_expression(item, kind, "5.."), legend_format(item, "服务端错误 (5xx)"), 1),
        target(router_response_ratio_expression(item, kind, "429"), legend_format(item, "限流 (429)"), 2),
    ]
    panel["fieldConfig"]["defaults"]["custom"] = timeseries_custom_options()
    panel["options"] = timeseries_options()
    panel["type"] = "timeseries"
    return panel


def topk_table_panel(item, panel_id, x, y, width, kind):
    panel = panel_base(item, panel_id, x, y, width, metric_unit(item))
    panel["description"] += (
        "\n- 展示口径：按单条原始标签序列计算每秒速率，仅展示当前值最高的 10 条；"
        "表格保留 Worker、模型、接口和错误类型等 exporter 实际提供的标签。"
    )
    raw_expression = "topk(10, rate({0}{{{1}}}[$__rate_interval]))".format(
        item["name"], selector(item, kind)
    )
    baseline = LAZY_COUNTER_BASELINES.get(item["name"])
    if baseline:
        raw_expression = "({0}) or ({1})".format(
            raw_expression,
            "sum by ({0}) (rate({1}{{{2}}}[$__rate_interval])) * 0".format(
                aggregation_labels(item), baseline, selector(item, kind)
            ),
        )
        panel["description"] += (
            "\n- 零值语义：原 Counter 未注册但基准请求 Counter 存在时显示 0；"
            "两者都不存在时仍显示 No data，应检查采集健康或版本支持。"
        )
    query = target(
        raw_expression,
        legend_format(item),
        0,
        instant=True,
    )
    query["format"] = "table"
    panel["targets"] = [query]
    panel["options"] = {
        "cellHeight": "sm",
        "footer": {"countRows": False, "fields": "", "reducer": ["sum"], "show": False},
        "showHeader": True,
    }
    panel["type"] = "table"
    return panel


def worker_health_panel(item, panel_id, x, y, width, kind):
    panel = panel_base(item, panel_id, x, y, width, "short")
    panel["title"] = "健康 Worker 总数"
    panel["description"] += (
        "\n- 聚合口径：对 `smg_worker_health` 求和；当前 exporter 未提供 `worker_type` 和模型标签，"
        "因此不能准确拆分 Prefill/Decode 或模型。"
    )
    panel["targets"] = [target(
        "sum by ({0}) ({1}{{{2}}})".format(
            aggregation_labels(item), item["name"], selector(item, kind)
        ),
        legend_format(item),
        0,
        instant=True,
    )]
    panel["options"] = {
        "colorMode": "value",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
        "textMode": "auto",
        "wideLayout": True,
    }
    panel["type"] = "stat"
    return panel


def metric_panel(item, panel_id, x, y, width, kind):
    name = item["name"]
    if name == "sglang:prompt_tokens_histogram":
        return token_distribution_panel(item, panel_id, x, y, width, kind, INPUT_TOKEN_BUCKETS)
    if name == "sglang:generation_tokens_histogram":
        return token_distribution_panel(item, panel_id, x, y, width, kind, GENERATION_TOKEN_BUCKETS)
    if name == "sglang:uncached_prompt_tokens_histogram":
        return cache_hit_panel(item, panel_id, x, y, width, kind)
    if name == "smg_http_responses_total":
        return router_response_outcome_panel(item, panel_id, x, y, width, kind)
    if name in {
        "smg_router_request_errors_total",
        "smg_worker_errors_total",
        "smg_worker_retries_exhausted_total",
        "smg_worker_cb_transitions_total",
        "smg_worker_cb_outcomes_total",
    }:
        return topk_table_panel(item, panel_id, x, y, width, kind)
    if name == "smg_worker_health":
        return worker_health_panel(item, panel_id, x, y, width, kind)

    panel = panel_base(item, panel_id, x, y, width, metric_unit(item))
    if kind == "split-router" and name == "sglang:num_requests_total":
        panel["title"] = "阶段完成速率"
        panel["description"] += (
            "\n- PD 分离口径：这是各阶段完成速率，不是可相加的端到端客户 RPS；"
            "客户请求速率请查看 Router 的 `smg_router_requests_total`。"
        )
    fixed_role = SPLIT_ROLE_METRICS.get(name) if kind == "split-router" else None
    if fixed_role:
        panel["description"] += (
            "\n- 固定角色：此面板只查询 `{0}`；Role 变量未选择该角色时不返回数据。"
        ).format(fixed_role)
    if item["type"] == "histogram":
        if name in SLO_LATENCY_METRICS:
            panel["targets"] = [
                target(
                    recorded_latency_expression(item, kind, quantile),
                    legend_format(item, label),
                    index,
                )
                for index, (quantile, label) in enumerate((
                    ("0.50", "P50"), ("0.95", "P95"), ("0.99", "P99"),
                ))
            ]
            panel["description"] += (
                "\n- 值班口径：展示 P50、P95 和 P99，不使用平均值掩盖长尾。"
                "\n- 查询来源：优先使用 30 秒计算一次的 5 分钟 recording rules；"
                "历史时间早于规则创建时间时，自动回退到原始 Histogram buckets。"
            )
            panel["x-querySource"] = "recording-rule-with-raw-fallback"
        else:
            panel["targets"] = [
                target(
                    histogram_quantile_expression(item, kind, "0.95"),
                    legend_format(item, "P95"),
                    0,
                ),
                target(
                    histogram_mean_expression(item, kind),
                    legend_format(item, "平均值 (Mean)"),
                    1,
                ),
            ]
    else:
        legend = (
            legend_format(item, "{{quantile}}")
            if item["type"] == "summary"
            else legend_format(item)
        )
        panel["targets"] = [target(expression(item, kind), legend, 0, name in STATIC_METRICS)]

    if name in STATIC_METRICS:
        panel["options"] = {
            "colorMode": "value",
            "graphMode": "none",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "textMode": "auto",
            "wideLayout": True,
        }
        panel["type"] = "stat"
        return panel

    panel["fieldConfig"]["defaults"]["custom"] = timeseries_custom_options()
    panel["options"] = timeseries_options()
    panel["type"] = "timeseries"
    return panel


def row_panel(title, panel_id, y):
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "panels": [],
        "title": category_title(title),
        "type": "row",
    }


def health_selector(kind):
    labels = ['job="file_sd_nodes"', 'expected="true"', 'instance=~"$instance"']
    if kind == "unified":
        labels.append('role="sglang-unified"')
    elif kind == "split-router":
        labels.append('role=~"$role"')
    else:
        raise ValueError("unsupported dashboard kind: {0}".format(kind))
    return ",".join(labels)


def health_panel(title, description, expression_value, legend, panel_id, x, y, width,
                 unit="short", panel_type="timeseries", instant=False,
                 thresholds=None, mappings=None):
    defaults = {
        "color": {"mode": "thresholds" if thresholds else "palette-classic"},
        "min": 0,
        "unit": unit,
    }
    if thresholds:
        defaults["thresholds"] = {"mode": "absolute", "steps": thresholds}
    if mappings:
        defaults["mappings"] = mappings
    if unit == "percentunit":
        defaults["max"] = 1
    panel = {
        "datasource": datasource(),
        "description": description,
        "fieldConfig": {
            "defaults": defaults,
            "overrides": [],
        },
        "gridPos": {"h": 8, "w": width, "x": x, "y": y},
        "id": panel_id,
        "targets": [target(expression_value, legend, 0, instant=instant)],
        "title": title,
        "type": panel_type,
        "x-panelKind": "scrape-health",
    }
    if panel_type == "stat":
        panel["options"] = {
            "colorMode": "value",
            "graphMode": "none",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "textMode": "auto",
            "wideLayout": True,
        }
    else:
        panel["fieldConfig"]["defaults"]["custom"] = timeseries_custom_options()
        panel["options"] = timeseries_options()
    return panel


def health_panels(kind, first_panel_id, y, compact=False):
    labels = health_selector(kind)
    role_instance = "{{role}} / {{instance}}"
    panels = [
        {
            "collapsed": False,
            "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
            "id": first_panel_id,
            "panels": [],
            "title": "采集健康 (Scrape Health)",
            "type": "row",
            "x-panelKind": "scrape-health",
        },
        health_panel(
            "采集目标状态（1 为 UP，0 为 DOWN）",
            "Prometheus `up` 指标。值为 0 表示目标存在但抓取失败；目标完全消失时，请结合“采集目标缺失状态”判断配置或服务发现异常。",
            "max by (role, instance) (up{{{0}}})".format(labels),
            role_instance,
            first_panel_id + 1, 0, y + 1, 6, panel_type="stat", instant=True,
            thresholds=[{"color": "red", "value": None}, {"color": "green", "value": 1}],
            mappings=[{"options": {
                "0": {"color": "red", "index": 0, "text": "DOWN"},
                "1": {"color": "green", "index": 1, "text": "UP"},
            }, "type": "value"}],
        ),
        health_panel(
            "纳管目标数",
            "统计带有 `expected=\"true\"` 且匹配当前变量的 SGLang target。Prometheus 无法知道未写入服务发现文件的外部期望数量。",
            "count(up{{{0}}})".format(labels),
            "纳管",
            first_panel_id + 2, 6, y + 1, 6, panel_type="stat", instant=True,
        ),
        health_panel(
            "最近成功采集距今时间",
            "根据最近 24 小时 `up == 1` 的样本计算。持续增大表示成功采集中断；No data 表示最近 24 小时没有成功样本。",
            "time() - max_over_time(timestamp((up{{{0}}} == 1))[24h:])".format(labels),
            role_instance,
            first_panel_id + 3, 12, y + 1, 12, unit="s", panel_type="stat", instant=True,
            thresholds=[
                {"color": "green", "value": None},
                {"color": "yellow", "value": 30},
                {"color": "red", "value": 60},
            ],
        ),
        health_panel(
            "每次采集样本数（Prometheus 单次抓取接收的样本数量）",
            "Prometheus `scrape_samples_scraped` 指标。突然降为 0 或明显下降可能表示 exporter 异常、指标注册变化或角色/版本变化。",
            "max by (role, instance) (scrape_samples_scraped{{{0}}})".format(labels),
            role_instance,
            first_panel_id + 4, 0, y + 9, 12,
        ),
        health_panel(
            "采集耗时（Prometheus 完成单次抓取所需秒数）",
            "Prometheus `scrape_duration_seconds` 指标。用于识别 exporter 响应变慢或抓取接近超时。",
            "max by (role, instance) (scrape_duration_seconds{{{0}}})".format(labels),
            role_instance,
            first_panel_id + 5, 12, y + 9, 12, unit="s",
        ),
        health_panel(
            "SGLang 记录规则数量",
            "Prometheus 自监控指标 `prometheus_rule_group_rules`。当前规则模板应报告 41 条；这比统计输出时序更能识别规则组是否加载。",
            'max(prometheus_rule_group_rules{rule_group=~".*;sglang[.]recording"})',
            "规则数",
            first_panel_id + 6, 0, y + 17, 12, panel_type="stat", instant=True,
        ),
        health_panel(
            "规则评估失败增量",
            "最近 5 分钟 SGLang recording rule 评估失败次数。0 为正常；大于 0 时应检查 Prometheus Rules 页面和日志。",
            'sum(increase(prometheus_rule_evaluation_failures_total{rule_group=~".*;sglang[.]recording"}[5m]))',
            "失败次数",
            first_panel_id + 7, 12, y + 17, 12, panel_type="stat", instant=True,
            thresholds=[{"color": "green", "value": None}, {"color": "red", "value": 1}],
        ),
    ]
    if compact:
        panels = [panels[index] for index in (0, 1, 3, 7)]
        for index, panel in enumerate(panels):
            panel["id"] = first_panel_id + index
        for index, panel in enumerate(panels[1:]):
            panel["gridPos"].update({"x": index * 8, "y": y + 1, "w": 8})
    return panels


def recording_panel(definition, panel_id, x, y):
    panel_type = definition.get("type", "timeseries")
    panel = {
        "datasource": datasource(),
        "description": definition["description"],
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "palette-classic"},
                "min": 0,
                "unit": definition.get("unit", "short"),
            },
            "overrides": [],
        },
        "gridPos": {"h": 8, "w": 12, "x": x, "y": y},
        "id": panel_id,
        "targets": [target(
            "({0}) or ({1})".format(definition["expr"], definition["fallback"]),
            definition["legend"], 0,
            instant=panel_type == "stat",
        )],
        "title": definition["title"],
        "type": panel_type,
        "x-panelKind": "derived",
    }
    if definition.get("unit") == "percentunit":
        panel["fieldConfig"]["defaults"]["max"] = 1
    if panel_type == "stat":
        panel["options"] = {
            "colorMode": "value",
            "graphMode": "none",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "textMode": "auto",
            "wideLayout": True,
        }
    else:
        panel["fieldConfig"]["defaults"]["custom"] = timeseries_custom_options()
        panel["options"] = timeseries_options()
    return panel


def derived_row(title, panel_id, y):
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "panels": [],
        "title": title,
        "type": "row",
        "x-panelKind": "derived",
    }


def derived_panels(first_panel_id, y):
    pd_definitions = [
        {
            "title": "Prefill/Decode 吞吐比",
            "description": "计算公式：Prefill 阶段完成速率 / Decode 阶段完成速率，按模型聚合；接近 1 通常表示两阶段吞吐匹配。该指标是跨角色全局指标，不受 Role/Instance 变量影响。优先查询 recording rule，旧时间窗自动回退原始 Counter。",
            "expr": 'my_prometheus:sglang_prefill_decode_throughput_ratio:5m{model_name=~"$model"}',
            "fallback": 'sum by (model_name) (rate(sglang:num_requests_total{role="sglang-prefill",model_name=~"$model"}[$__rate_interval])) / clamp_min(sum by (model_name) (rate(sglang:num_requests_total{role="sglang-decode",model_name=~"$model"}[$__rate_interval])), 1e-9)',
            "legend": "{{model_name}}",
        },
        {
            "title": "Prefill/Decode Worker 容量比",
            "description": "计算公式：Router 注册的 Prefill Worker 数 / Decode Worker 数；接近 1 表示两类 Worker 数量相当，但正常区间仍取决于单 Worker 容量。仅在 Role 选择包含 Router 时展示。",
            "expr": 'my_prometheus:sglang_prefill_decode_worker_capacity_ratio{role=~"$role",instance=~"$instance",model=~"$model"}',
            "fallback": 'sum by (role, instance, model) (smg_worker_pool_size{role=~"$role",role="sglang-router",instance=~"$instance",model=~"$model",worker_type="prefill"}) / clamp_min(sum by (role, instance, model) (smg_worker_pool_size{role=~"$role",role="sglang-router",instance=~"$instance",model=~"$model",worker_type="decode"}), 1)',
            "legend": "{{role}} / {{instance}} / {{model}}",
        },
        {
            "title": "KV 传输失败率",
            "description": "计算公式：KV 传输失败速率 / 相同 Role、Instance、Model 的阶段完成速率。0 表示窗口内无失败，越低越好；未配置业务告警阈值。旧时间窗回退原始 Counter。",
            "expr": 'my_prometheus:sglang_kv_transfer_failure_ratio:5m{role=~"$role",instance=~"$instance",model_name=~"$model"}',
            "fallback": '(sum by (role, instance, model_name) (rate(sglang:num_transfer_failed_reqs_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) or sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) * 0) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])), 1e-9)',
            "legend": "{{role}} / {{instance}} / {{model_name}}",
            "unit": "percentunit",
        },
        {
            "title": "Bootstrap 失败率",
            "description": "计算公式：Bootstrap 失败速率 / 相同阶段完成速率。0 表示窗口内无失败，越低越好；未配置业务告警阈值。旧时间窗回退原始 Counter。",
            "expr": 'my_prometheus:sglang_bootstrap_failure_ratio:5m{role=~"$role",instance=~"$instance",model_name=~"$model"}',
            "fallback": '(sum by (role, instance, model_name) (rate(sglang:num_bootstrap_failed_reqs_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) or sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) * 0) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])), 1e-9)',
            "legend": "{{role}} / {{instance}} / {{model_name}}",
            "unit": "percentunit",
        },
        {
            "title": "Prefill 重试率",
            "description": "计算公式：Prefill 重试速率 / Prefill 完成速率。0 表示窗口内无重试，越低越好；仅 Role 选择包含 Prefill 时展示。",
            "expr": 'my_prometheus:sglang_prefill_retry_ratio:5m{role=~"$role",instance=~"$instance",model_name=~"$model"}',
            "fallback": '(sum by (role, instance, model_name) (rate(sglang:num_prefill_retries_total{role=~"$role",role="sglang-prefill",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) or sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",role="sglang-prefill",instance=~"$instance",model_name=~"$model"}[$__rate_interval])) * 0) / clamp_min(sum by (role, instance, model_name) (rate(sglang:num_requests_total{role=~"$role",role="sglang-prefill",instance=~"$instance",model_name=~"$model"}[$__rate_interval])), 1e-9)',
            "legend": "{{role}} / {{instance}} / {{model_name}}",
            "unit": "percentunit",
        },
        {
            "title": "KV 传输 P99 延迟",
            "description": "KV 传输耗时的 P99，单位毫秒，越低越好；具体健康区间需按链路 SLO 配置。旧时间窗回退原始 Histogram。",
            "expr": 'my_prometheus:sglang_kv_transfer_latency_ms_p99:5m{role=~"$role",instance=~"$instance",model_name=~"$model"}',
            "fallback": 'histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_latency_ms_bucket{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])))',
            "legend": "{{role}} / {{instance}} / {{model_name}}",
            "unit": "ms",
        },
        {
            "title": "KV 传输 P99 速度",
            "description": "KV 传输速度的 P99，单位 GB/s。应结合数据量和网络基线判断，不设置无依据的固定阈值；旧时间窗回退原始 Histogram。",
            "expr": 'my_prometheus:sglang_kv_transfer_speed_gb_s_p99:5m{role=~"$role",instance=~"$instance",model_name=~"$model"}',
            "fallback": 'histogram_quantile(0.99, sum by (role, instance, model_name, le) (rate(sglang:kv_transfer_speed_gb_s_bucket{role=~"$role",instance=~"$instance",model_name=~"$model"}[$__rate_interval])))',
            "legend": "{{role}} / {{instance}} / {{model_name}}",
            "unit": "suffix: GB/s",
        },
    ]
    router_definitions = [
        {
            "title": "Router 错误率",
            "description": "计算公式：Router 路由错误速率 / Router 客户请求速率。0 表示窗口内无错误，越低越好；未配置业务告警阈值。",
            "expr": 'my_prometheus:sglang_router_error_ratio:5m{role=~"$role",instance=~"$instance"}',
            "fallback": '(sum by (role, instance) (rate(smg_router_request_errors_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])) or sum by (role, instance) (rate(smg_router_requests_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])) * 0) / clamp_min(sum by (role, instance) (rate(smg_router_requests_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])), 1e-9)',
            "legend": "{{role}} / {{instance}}",
            "unit": "percentunit",
        },
        {
            "title": "重试耗尽率",
            "description": "计算公式：重试耗尽速率 / Router 客户请求速率。0 表示窗口内无耗尽，越低越好。",
            "expr": 'my_prometheus:sglang_router_retry_exhausted_ratio:5m{role=~"$role",instance=~"$instance"}',
            "fallback": '(sum by (role, instance) (rate(smg_worker_retries_exhausted_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])) or sum by (role, instance) (rate(smg_router_requests_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])) * 0) / clamp_min(sum by (role, instance) (rate(smg_router_requests_total{role=~"$role",role="sglang-router",instance=~"$instance"}[$__rate_interval])), 1e-9)',
            "legend": "{{role}} / {{instance}}",
            "unit": "percentunit",
        },
        {
            "title": "健康 Worker 总数",
            "description": "计算公式：对 Router 上报的 `smg_worker_health` 求和。必须大于 0；期望数量由实际部署拓扑决定。当前原指标无 Worker 类型和模型标签，不能准确拆分角色或模型。",
            "expr": 'my_prometheus:sglang_router_healthy_workers{role=~"$role",instance=~"$instance"}',
            "fallback": 'sum by (role, instance) (smg_worker_health{role=~"$role",role="sglang-router",instance=~"$instance"})',
            "legend": "{{role}} / {{instance}}",
            "type": "stat",
        },
        {
            "title": "打开的熔断器数量",
            "description": "计算公式：统计状态为 Open 的 Worker 熔断器。0 为正常；原指标状态 0/1/2 分别表示 Closed/Open/Half-open。",
            "expr": 'my_prometheus:sglang_router_open_circuit_breakers{role=~"$role",instance=~"$instance"}',
            "fallback": 'sum by (role, instance) (smg_worker_cb_state{role=~"$role",role="sglang-router",instance=~"$instance"} == bool 1)',
            "legend": "{{role}} / {{instance}}",
            "type": "stat",
        },
        {
            "title": "Worker 负载偏斜",
            "description": "Recording rule：`my_prometheus:sglang_router_worker_load_skew`。接近 1 表示较均衡，升高表示最忙 Worker 明显高于平均值。",
            "expr": 'my_prometheus:sglang_router_worker_load_skew{role=~"$role",instance=~"$instance"}',
            "fallback": 'max by (role, instance) (smg_worker_requests_active{role=~"$role",role="sglang-router",instance=~"$instance"}) / clamp_min(avg by (role, instance) (smg_worker_requests_active{role=~"$role",role="sglang-router",instance=~"$instance"}), 1e-9)',
            "legend": "{{role}} / {{instance}}",
        },
    ]

    panels = []
    panel_id = first_panel_id
    current_y = y
    for title, definitions in (
        ("PD 链路派生指标 (PD Pipeline Derived Metrics)", pd_definitions),
        ("Router 可用性派生指标 (Router Availability Derived Metrics)", router_definitions),
    ):
        panels.append(derived_row(title, panel_id, current_y))
        panel_id += 1
        current_y += 1
        for index, definition in enumerate(definitions):
            x = 0 if index % 2 == 0 else 12
            panels.append(recording_panel(definition, panel_id, x, current_y))
            panel_id += 1
            if index % 2 == 1:
                current_y += 8
        if len(definitions) % 2:
            current_y += 8
    return panels, panel_id, current_y


def info_panel(title, role_text, metric_count, panel_id, y):
    translation = TRANSLATIONS["dashboards"][title]
    display_title = bilingual(translation["title"], title)
    content = (
        "# {0}\n\n"
        "覆盖 **{1} 个指标族**。{2} 数据源：`{3}`。"
        "先用“采集健康”区分抓取故障，再判断未启用、版本未暴露或零事件。"
        "少数跨角色派生指标不受全部变量控制，具体范围见面板 Tooltip。"
    ).format(display_title, metric_count, translation["description"], DATASOURCE_UID)
    return {
        "gridPos": {"h": 3, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "options": {"content": content, "mode": "markdown"},
        "title": "看板范围 (Dashboard Scope)",
        "type": "text",
    }


def query_variable(name, label, query, multi=True):
    return {
        "allValue": ".*" if multi else None,
        "current": {},
        "datasource": datasource(),
        "definition": query,
        "hide": 0,
        "includeAll": multi,
        "label": bilingual({"Role": "角色", "Instance": "实例", "Model": "模型"}[label], label),
        "multi": multi,
        "name": name,
        "options": [],
        "query": {"query": query, "refId": "Variable-{0}".format(name)},
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "sort": 1,
        "type": "query",
    }


def variables(kind):
    if kind == "unified":
        return [
            query_variable(
                "instance", "Instance",
                'label_values(up{job="file_sd_nodes",expected="true",role="sglang-unified"}, instance)',
            ),
            query_variable(
                "model", "Model",
                'label_values(sglang:num_requests_total{instance=~"$instance",role="sglang-unified",engine_type="unified"}, model_name)',
            ),
        ]
    if kind == "split-router":
        return [
            query_variable(
                "role", "Role",
                'label_values(up{job="file_sd_nodes",expected="true",role=~"sglang-prefill|sglang-decode|sglang-router"}, role)',
            ),
            query_variable(
                "instance", "Instance",
                'label_values(up{job="file_sd_nodes",expected="true",role=~"$role"}, instance)',
            ),
            query_variable(
                "model", "Model",
                'label_values(sglang:num_requests_total{instance=~"$instance",role=~"$role",engine_type=~"prefill|decode"}, model_name)',
            ),
        ]
    raise ValueError("unsupported dashboard kind: {0}".format(kind))


def build_dashboard(kind, title, uid, groups, role_text, expanded_groups=None,
                    refresh="1m", include_derived=False, compact_health=False):
    catalog = flatten(groups)
    expanded_groups = set(expanded_groups or ())
    panels = []
    panel_id = 1
    y = 0
    panels.append(info_panel(title, role_text, len(catalog), panel_id, y))
    panel_id += 1
    y += 3

    scrape_health_panels = health_panels(kind, panel_id, y, compact=compact_health)
    panels.extend(scrape_health_panels)
    panel_id += len(scrape_health_panels)
    y += 9 if compact_health else 25

    for group_title, items in groups.items():
        row = row_panel(group_title, panel_id, y)
        row["collapsed"] = group_title not in expanded_groups
        panels.append(row)
        panel_id += 1
        y += 1
        x = 0
        row_height = 8
        for item in items:
            if item["name"] in STATIC_METRICS:
                panel_width = 6
            elif group_title in ("Key Engine Metrics", "Key Router Metrics"):
                panel_width = 8
            else:
                panel_width = 12
            if x + panel_width > 24:
                x = 0
                y += row_height
            metric = metric_panel(item, panel_id, x, y, panel_width, kind)
            if row["collapsed"]:
                row["panels"].append(metric)
            else:
                panels.append(metric)
            panel_id += 1
            x += panel_width
        y += row_height
        if include_derived and group_title == "Key Router Metrics":
            extra_panels, panel_id, y = derived_panels(panel_id, y)
            panels.extend(extra_panels)

    return {
        "annotations": {"list": []},
        "description": "{0} {1} 使用共享 Prometheus 数据源和按角色区分的采集目标。".format(
            bilingual(TRANSLATIONS["dashboards"][title]["title"], title),
            TRANSLATIONS["dashboards"][title]["description"],
        ),
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 1,
        "id": None,
        "links": [{
            "asDropdown": True,
            "icon": "external link",
            "includeVars": True,
            "keepTime": True,
            "tags": ["sglang-operations"],
            "targetBlank": False,
            "title": "SGLang 运维看板",
            "type": "dashboards",
        }],
        "liveNow": False,
        "panels": panels,
        "refresh": refresh,
        "schemaVersion": 39,
        "tags": ["sglang", "sglang-operations", kind, "prometheus"],
        "templating": {"list": variables(kind)},
        "time": {"from": "now-6h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": bilingual(TRANSLATIONS["dashboards"][title]["title"], title),
        "uid": uid,
        "version": 1,
        "weekStart": "",
        "x-metricsCatalog": catalog,
    }


def write_dashboard(filename, dashboard):
    path = OUTPUT_DIR / filename
    with open(str(path), "w") as handle:
        json.dump(dashboard, handle, indent=2, sort_keys=False)
        handle.write("\n")


def validate_catalog(groups, expected_count):
    items = flatten(groups)
    names = [item["name"] for item in items]
    if len(names) != expected_count:
        raise RuntimeError("expected {0} metrics, found {1}".format(expected_count, len(names)))
    if len(names) != len(set(names)):
        duplicates = sorted(name for name in set(names) if names.count(name) > 1)
        raise RuntimeError("duplicate metrics: {0}".format(", ".join(duplicates)))


def selected_groups(*names):
    combined = {}
    combined.update(ENGINE_GROUPS)
    combined.update(ROUTER_GROUPS)
    return OrderedDict((name, combined[name]) for name in names)


def selected_metric_groups(*definitions):
    lookup = {
        item["name"]: item
        for item in flatten(ENGINE_GROUPS) + flatten(ROUTER_GROUPS)
    }
    return OrderedDict(
        (title, [lookup[name] for name in names])
        for title, names in definitions
    )


def main():
    validate_catalog(ENGINE_GROUPS, 122)
    validate_catalog(ROUTER_GROUPS, 61)
    validate_translations(
        TRANSLATIONS,
        (
            "SGLang PD Unified Metrics",
            "SGLang PD Disaggregated and Router Metrics",
            "SGLang Service Overview",
            "SGLang PD Pipeline",
            "SGLang Engine and Scheduler",
            "SGLang Router and Worker",
            "SGLang KV and Capacity",
            "SGLang Optional Features",
        ),
        list(ENGINE_GROUPS) + list(ROUTER_GROUPS),
        [item["name"] for item in flatten(ENGINE_GROUPS) + flatten(ROUTER_GROUPS)],
    )
    write_dashboard(
        "sglang-pd-unified.json",
        build_dashboard(
            "unified", "SGLang PD Unified Metrics", "my-prometheus-sglang-pd-unified",
            ENGINE_GROUPS, "a unified prefill/decode engine",
            expanded_groups=("Key Engine Metrics", "Request Latency Pipeline"),
        ),
    )
    split_router_groups = OrderedDict()
    for group_name in ("Key Engine Metrics", "Key Router Metrics"):
        source = ENGINE_GROUPS if group_name in ENGINE_GROUPS else ROUTER_GROUPS
        split_router_groups[group_name] = source[group_name]
    for source in (ENGINE_GROUPS, ROUTER_GROUPS):
        for group_name, items in source.items():
            if group_name not in split_router_groups:
                split_router_groups[group_name] = items
    write_dashboard(
        "sglang-pd-disaggregated.json",
        build_dashboard(
            "split-router", "SGLang PD Disaggregated and Router Metrics",
            "my-prometheus-sglang-pd-disaggregated", split_router_groups,
            "separate prefill/decode engines, the Router, and Router Mesh; select one or more "
            "roles, or All, from the Role variable (panels without matching metrics show no data)",
            expanded_groups=(
                "Key Engine Metrics", "Key Router Metrics", "Request Latency Pipeline",
            ),
            include_derived=True,
        ),
    )

    operational_dashboards = (
        (
            "sglang-service-overview.json", "SGLang Service Overview",
            "my-prometheus-sglang-service-overview",
            selected_metric_groups(
                ("Key Engine Metrics", (
                    "sglang:prompt_tokens_total",
                    "sglang:generation_tokens_total",
                    "sglang:num_aborted_requests_total",
                    "sglang:num_running_reqs",
                    "sglang:num_queue_reqs",
                    "sglang:token_usage",
                    "sglang:time_to_first_token_seconds",
                    "sglang:inter_token_latency_seconds",
                    "sglang:e2e_request_latency_seconds",
                    "sglang:num_transfer_failed_reqs_total",
                )),
                ("Key Router Metrics", (
                    "smg_router_requests_total",
                    "smg_http_responses_total",
                    "smg_worker_health",
                )),
            ),
            ("Key Engine Metrics", "Key Router Metrics"), "30s", False,
        ),
        (
            "sglang-pd-pipeline.json", "SGLang PD Pipeline",
            "my-prometheus-sglang-pd-pipeline",
            selected_groups("Request Latency Pipeline", "PD Queues and KV Transfer"),
            ("Request Latency Pipeline", "PD Queues and KV Transfer"), "30s", False,
        ),
        (
            "sglang-engine-scheduler.json", "SGLang Engine and Scheduler",
            "my-prometheus-sglang-engine-scheduler",
            selected_groups(
                "HTTP, Process and Functions", "Requests, Tokens and User Latency",
                "Scheduler State", "Retraction, Queue and Stage Latency",
            ),
            ("Scheduler State",), "1m", False,
        ),
        (
            "sglang-router-worker.json", "SGLang Router and Worker",
            "my-prometheus-sglang-router-worker",
            selected_groups(
                "Key Router Metrics", "Router Request Latency Pipeline",
                "HTTP and Router Requests", "Worker Pool and Health",
                "Policies, Circuit Breaker and Retries",
            ),
            ("Key Router Metrics",), "1m", False,
        ),
        (
            "sglang-kv-capacity.json", "SGLang KV and Capacity",
            "my-prometheus-sglang-kv-capacity",
            selected_groups(
                "KV, SWA and Mamba Pools", "CUDA, Tokens and MFU Runtime",
                "Engine Capacity and Startup", "PD Queues and KV Transfer",
                "Prefix Cache and Routing Keys",
            ),
            ("KV, SWA and Mamba Pools",), "1m", False,
        ),
        (
            "sglang-optional-features.json", "SGLang Optional Features",
            "my-prometheus-sglang-optional-features",
            selected_groups(
                "Grammar", "Speculative Decoding and Prefill Delayer",
                "Optional LoRA, HiCache, Streaming and EPLB",
                "Discovery, MCP and Persistence", "Router Mesh",
            ),
            (), "1m", False,
        ),
    )
    for filename, title, uid, groups, expanded, refresh, include_derived in operational_dashboards:
        write_dashboard(
            filename,
            build_dashboard(
                "split-router", title, uid, groups,
                "the selected SGLang operational scope",
                expanded_groups=expanded,
                refresh=refresh,
                include_derived=include_derived,
                compact_health=filename == "sglang-service-overview.json",
            ),
        )


if __name__ == "__main__":
    main()
