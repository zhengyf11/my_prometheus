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
    "sglang:num_running_reqs",
    "sglang:num_queue_reqs",
    "sglang:gen_throughput",
    "sglang:cache_hit_rate",
    "sglang:token_usage",
    "sglang:utilization",
)

ENGINE_LATENCY_METRICS = (
    "sglang:queue_time_seconds",
    "sglang:prefill_delayer_wait_seconds",
    "sglang:kv_transfer_bootstrap_ms",
    "sglang:kv_transfer_alloc_ms",
    "sglang:kv_transfer_latency_ms",
    "sglang:per_stage_req_latency_seconds",
    "sglang:time_to_first_token_seconds",
    "sglang:inter_token_latency_seconds",
    "sglang:e2e_request_latency_seconds",
)

KEY_ROUTER_METRICS = (
    "smg_http_requests_total",
    "smg_http_connections_active",
    "smg_router_requests_total",
    "smg_router_request_errors_total",
    "smg_worker_pool_size",
    "smg_worker_requests_active",
    "smg_worker_health",
)

ROUTER_LATENCY_METRICS = (
    "smg_http_request_duration_seconds",
    "smg_router_request_duration_seconds",
    "smg_router_stage_duration_seconds",
    "smg_router_ttft_seconds",
    "smg_router_tpot_seconds",
    "smg_router_generation_duration_seconds",
)

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
        title, explanation = rate_display(item)
        return "{0}（{1}）".format(title, explanation)
    translation = metric_translation(item)
    return "{0}（{1}）".format(translation["title"], short_explanation(item))


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
        return "sum by ({0}) (rate({1}{{{2}}}[$__rate_interval]))".format(
            aggregation_labels(item), name, labels
        )
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
            "calcs": ["lastNotNull", "mean"],
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
    return {
        "datasource": datasource(),
        "description": metric_mapping(item),
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "palette-classic"},
                "unit": unit,
            },
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
    panel["title"] = "输入 Token 缓存命中率（由总输入与未缓存输入 Token 计算）"
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


def metric_panel(item, panel_id, x, y, width, kind):
    name = item["name"]
    if name == "sglang:prompt_tokens_histogram":
        return token_distribution_panel(item, panel_id, x, y, width, kind, INPUT_TOKEN_BUCKETS)
    if name == "sglang:generation_tokens_histogram":
        return token_distribution_panel(item, panel_id, x, y, width, kind, GENERATION_TOKEN_BUCKETS)
    if name == "sglang:uncached_prompt_tokens_histogram":
        return cache_hit_panel(item, panel_id, x, y, width, kind)

    panel = panel_base(item, panel_id, x, y, width, metric_unit(item))
    if item["type"] == "histogram":
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
    labels = ['job="file_sd_nodes"', 'instance=~"$instance"']
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
        "unit": unit,
    }
    if thresholds:
        defaults["thresholds"] = {"mode": "absolute", "steps": thresholds}
    if mappings:
        defaults["mappings"] = mappings
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


def health_panels(kind, first_panel_id, y):
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
            "采集目标缺失状态（1 为缺失，0 为已发现）",
            "使用 `absent(up)` 判断所选 Role/Instance 是否完全没有匹配目标。值为 1 时应检查 target 文件、标签和变量选择。",
            "clamp_max(absent(up{{{0}}}), 1) or on() (count(up{{{0}}}) * 0)".format(labels),
            "目标缺失状态",
            first_panel_id + 2, 6, y + 1, 6, panel_type="stat", instant=True,
            thresholds=[{"color": "green", "value": None}, {"color": "red", "value": 1}],
            mappings=[{"options": {
                "0": {"color": "green", "index": 0, "text": "已发现"},
                "1": {"color": "red", "index": 1, "text": "缺失"},
            }, "type": "value"}],
        ),
        health_panel(
            "最近成功采集距今时间（24 小时内最后一次 UP 距今秒数）",
            "根据最近 24 小时 `up == 1` 的样本计算。持续增大表示成功采集中断；No data 表示最近 24 小时没有成功样本。",
            "time() - max_over_time(timestamp((up{{{0}}} == 1))[24h:])".format(labels),
            role_instance,
            first_panel_id + 3, 12, y + 1, 12, unit="s", panel_type="stat", instant=True,
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
    ]
    return panels


def info_panel(title, role_text, metric_count, panel_id, y):
    translation = TRANSLATIONS["dashboards"][title]
    display_title = bilingual(translation["title"], title)
    content = (
        "# {0}\n\n"
        "本看板覆盖 **{1} 个指标族**。{2} "
        "看板使用共享 Prometheus 数据源 `{3}`，并通过 SGLang `role` 标签选择采集目标。"
        "面板显示 No data 时，必须先查看“采集健康”分组：它既可能表示角色不适用或功能未启用，也可能表示抓取失败、目标消失、标签变化或实例退出。"
        "PD 分离与 Router 看板会把 Role 直接加入每条 PromQL；不匹配所选 Role 的指标面板会显示 No data。"
    ).format(display_title, metric_count, translation["description"], DATASOURCE_UID)
    return {
        "gridPos": {"h": 5, "w": 24, "x": 0, "y": y},
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
                'label_values(up{job="file_sd_nodes",role="sglang-unified"}, instance)',
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
                'label_values(up{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode|sglang-router"}, role)',
            ),
            query_variable(
                "instance", "Instance",
                'label_values(up{job="file_sd_nodes",role=~"$role"}, instance)',
            ),
            query_variable(
                "model", "Model",
                'label_values(sglang:num_requests_total{instance=~"$instance",role=~"$role",engine_type=~"prefill|decode"}, model_name)',
            ),
        ]
    raise ValueError("unsupported dashboard kind: {0}".format(kind))


def build_dashboard(kind, title, uid, groups, role_text):
    catalog = flatten(groups)
    panels = []
    panel_id = 1
    y = 0
    panels.append(info_panel(title, role_text, len(catalog), panel_id, y))
    panel_id += 1
    y += 5

    scrape_health_panels = health_panels(kind, panel_id, y)
    panels.extend(scrape_health_panels)
    panel_id += len(scrape_health_panels)
    y += 17

    for group_title, items in groups.items():
        panels.append(row_panel(group_title, panel_id, y))
        panel_id += 1
        y += 1
        x = 0
        row_height = 8
        for item in items:
            panel_width = 6 if item["name"] in STATIC_METRICS else 12
            if x + panel_width > 24:
                x = 0
                y += row_height
            panels.append(metric_panel(item, panel_id, x, y, panel_width, kind))
            panel_id += 1
            x += panel_width
        y += row_height

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
        "links": [],
        "liveNow": False,
        "panels": panels,
        "refresh": "30s",
        "schemaVersion": 39,
        "tags": ["sglang", kind, "complete-metrics", "prometheus"],
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


def main():
    validate_catalog(ENGINE_GROUPS, 122)
    validate_catalog(ROUTER_GROUPS, 61)
    validate_translations(
        TRANSLATIONS,
        ("SGLang PD Unified Metrics", "SGLang PD Disaggregated and Router Metrics"),
        list(ENGINE_GROUPS) + list(ROUTER_GROUPS),
        [item["name"] for item in flatten(ENGINE_GROUPS) + flatten(ROUTER_GROUPS)],
    )
    write_dashboard(
        "sglang-pd-unified.json",
        build_dashboard(
            "unified", "SGLang PD Unified Metrics", "my-prometheus-sglang-pd-unified",
            ENGINE_GROUPS, "a unified prefill/decode engine",
        ),
    )
    split_router_groups = OrderedDict()
    split_router_groups.update(ENGINE_GROUPS)
    split_router_groups.update(ROUTER_GROUPS)
    write_dashboard(
        "sglang-pd-disaggregated.json",
        build_dashboard(
            "split-router", "SGLang PD Disaggregated and Router Metrics",
            "my-prometheus-sglang-pd-disaggregated", split_router_groups,
            "separate prefill/decode engines, the Router, and Router Mesh; select one or more "
            "roles, or All, from the Role variable (panels without matching metrics show no data)",
        ),
    )


if __name__ == "__main__":
    main()
