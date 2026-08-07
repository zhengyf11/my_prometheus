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


def flatten(groups):
    return [item for items in groups.values() for item in items]


def datasource():
    return {"type": "prometheus", "uid": DATASOURCE_UID}


def category_title(original):
    return bilingual(TRANSLATIONS["categories"][original], original)


def metric_title(item):
    translation = TRANSLATIONS["metrics"][item["name"]]
    return bilingual(translation["title"], item["name"])


def selector(item, kind):
    if item["name"].startswith(("smg_", "router_")):
        return 'instance=~"$instance"'
    return 'instance=~"$instance",model_name=~"$model|^$"'


def expression(item, kind):
    name = item["name"]
    metric_type = item["type"]
    labels = selector(item, kind)
    if metric_type == "counter":
        return "sum by (instance) (rate({0}{{{1}}}[$__rate_interval]))".format(name, labels)
    return "max by (instance) ({0}{{{1}}})".format(name, labels)


def histogram_quantile_expression(item, kind, quantile):
    return (
        "histogram_quantile({0}, sum by (instance, le) "
        "(rate({1}_bucket{{{2}}}[$__rate_interval])))"
    ).format(quantile, item["name"], selector(item, kind))


def histogram_mean_expression(item, kind):
    name = item["name"]
    labels = selector(item, kind)
    return (
        "sum by (instance) (rate({0}_sum{{{1}}}[$__rate_interval])) / "
        "clamp_min(sum by (instance) (rate({0}_count{{{1}}}[$__rate_interval])), 1e-9)"
    ).format(name, labels)


def ref_id(index):
    return "Q{0:02d}".format(index + 1)


def row_panel(title, panel_id, y):
    return {
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "id": panel_id,
        "panels": [],
        "title": category_title(title),
        "type": "row",
    }


def chart_panel(title, items, panel_id, x, y, width, kind):
    metric_type = items[0]["type"]
    suffix = {
        "counter": "速率 (Rate)",
        "gauge": "当前值 (Current State)",
        "histogram": "P80 / P95 / 平均值 (Mean)",
        "summary": "分位数 (Quantiles)",
    }[metric_type]
    targets = []
    for item in items:
        if item["type"] == "histogram":
            histogram_queries = (
                ("P80", histogram_quantile_expression(item, kind, "0.80")),
                ("P95", histogram_quantile_expression(item, kind, "0.95")),
                ("平均值 (Mean)", histogram_mean_expression(item, kind)),
            )
            for label, query in histogram_queries:
                targets.append({
                    "datasource": datasource(),
                    "expr": query,
                    "legendFormat": "{0} {{{{instance}}}} {1}".format(metric_title(item), label),
                    "refId": ref_id(len(targets)),
                })
        else:
            targets.append({
                "datasource": datasource(),
                "expr": expression(item, kind),
                "legendFormat": "{0} {{{{instance}}}}".format(metric_title(item)),
                "refId": ref_id(len(targets)),
            })
    return {
        "datasource": datasource(),
        "description": "\n".join(
            ["本面板包含以下指标；功能未启用或事件尚未发生时显示 No data 属于正常现象。", ""]
            + [
                "- {0}: {1}".format(
                    metric_title(item), TRANSLATIONS["metrics"][item["name"]]["description"]
                )
                for item in items
            ]
        ),
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {
                    "drawStyle": "line",
                    "fillOpacity": 10,
                    "lineWidth": 1,
                    "showPoints": "never",
                    "spanNulls": True,
                },
                "unit": "short",
            },
            "overrides": [],
        },
        "gridPos": {"h": 9, "w": width, "x": x, "y": y},
        "id": panel_id,
        "options": {
            "legend": {
                "calcs": ["lastNotNull", "mean"],
                "displayMode": "table",
                "placement": "bottom",
                "showLegend": True,
            },
            "tooltip": {"mode": "multi", "sort": "desc"},
        },
        "targets": targets,
        "title": suffix,
        "type": "timeseries",
    }


def info_panel(title, role_text, metric_count, panel_id, y):
    translation = TRANSLATIONS["dashboards"][title]
    display_title = bilingual(translation["title"], title)
    content = (
        "# {0}\n\n"
        "本看板覆盖 **{1} 个指标族**。{2} "
        "看板使用共享 Prometheus 数据源 `{3}`，并通过 SGLang `role` 标签选择采集目标。"
        "占位目标在对应进程启动前可以是 DOWN；指标按功能或事件延迟注册时，No data 属于正常现象。"
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
                'label_values(sglang:num_requests_total{instance=~"$instance",engine_type="unified"}, model_name)',
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
                'label_values(sglang:num_requests_total{instance=~"$instance",engine_type=~"prefill|decode"}, model_name)',
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

    for group_title, items in groups.items():
        panels.append(row_panel(group_title, panel_id, y))
        panel_id += 1
        y += 1
        by_type = OrderedDict()
        for item in items:
            by_type.setdefault(item["type"], []).append(item)
        width = 24 // len(by_type)
        x = 0
        for index, typed_items in enumerate(by_type.values()):
            panel_width = 24 - x if index == len(by_type) - 1 else width
            panels.append(chart_panel(group_title, typed_items, panel_id, x, y, panel_width, kind))
            panel_id += 1
            x += panel_width
        y += 9

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
