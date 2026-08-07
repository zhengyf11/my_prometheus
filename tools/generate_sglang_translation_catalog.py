#!/usr/bin/env python3
"""Generate a review catalog for optional Chinese SGLang dashboard labels."""

from pathlib import Path

from generate_sglang_dashboards import ENGINE_GROUPS, ROUTER_GROUPS


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "SGLang_Dashboard_中文翻译候选.md"

DASHBOARDS = (
    (
        "SGLang PD Unified Metrics",
        "SGLang PD 合部指标",
        "PD 合部",
        "展示 unified engine 的 122 个指标族。",
    ),
    (
        "SGLang PD Disaggregated and Router Metrics",
        "SGLang PD 分离与 Router 指标",
        "Prefill / Decode / Router",
        "通过 Role 下拉框选择 Prefill、Decode 或 Router，共覆盖 183 个指标族。",
    ),
)

CATEGORY_TRANSLATIONS = {
    "HTTP, Process and Functions": "HTTP、进程与函数",
    "Requests, Tokens and User Latency": "请求、Token 与用户延迟",
    "Scheduler State": "调度器状态",
    "KV, SWA and Mamba Pools": "KV、SWA 与 Mamba 资源池",
    "CUDA, Tokens and MFU Runtime": "CUDA、Token 与 MFU 运行时",
    "Engine Capacity and Startup": "引擎容量与启动",
    "Retraction, Queue and Stage Latency": "回退、队列与阶段延迟",
    "Grammar": "Grammar 结构化输出",
    "Speculative Decoding and Prefill Delayer": "投机解码与 Prefill 延迟器",
    "PD Queues and KV Transfer": "PD 队列与 KV 传输",
    "Prefix Cache and Routing Keys": "Prefix Cache 与路由键",
    "Optional LoRA, HiCache, Streaming and EPLB": "可选 LoRA、HiCache、流式会话与 EPLB",
    "HTTP and Router Requests": "HTTP 与 Router 请求",
    "Worker Pool and Health": "Worker 池与健康状态",
    "Policies, Circuit Breaker and Retries": "路由策略、熔断与重试",
    "Discovery, MCP and Persistence": "服务发现、MCP 与持久化",
    "Router Mesh": "Router Mesh 集群",
}

EXACT_TRANSLATIONS = {
    "time_to_first_token_seconds": "首 Token 延迟",
    "inter_token_latency_seconds": "Token 间延迟（TPOT/ITL）",
    "e2e_request_latency_seconds": "请求端到端延迟",
    "prompt_tokens_total": "输入 Token 总数",
    "generation_tokens_total": "生成 Token 总数",
    "prompt_tokens_histogram": "输入 Token 数分布",
    "uncached_prompt_tokens_histogram": "未缓存输入 Token 数分布",
    "generation_tokens_histogram": "生成 Token 数分布",
    "num_running_reqs": "运行中请求数",
    "num_queue_reqs": "排队请求数",
    "gen_throughput": "生成吞吐量",
    "cache_hit_rate": "缓存命中率",
    "token_usage": "Token 池使用率",
    "kv_available_tokens": "KV 可用 Token 数",
    "kv_evictable_tokens": "KV 可淘汰 Token 数",
    "kv_used_tokens": "KV 已用 Token 数",
    "engine_startup_time": "引擎启动耗时",
    "engine_load_weights_time": "引擎权重加载耗时",
    "startup_available_gpu_memory_gb": "启动时可用 GPU 显存",
    "queue_time_seconds": "请求排队耗时",
    "per_stage_req_latency_seconds": "请求各阶段延迟",
    "kv_transfer_speed_gb_s": "KV 传输速度",
    "kv_transfer_latency_ms": "KV 传输延迟",
    "kv_transfer_total_mb": "KV 传输数据量",
    "router_ttft_seconds": "Router 首 Token 延迟",
    "router_tpot_seconds": "Router Token 间延迟",
    "router_request_duration_seconds": "Router 请求耗时",
    "worker_health": "Worker 健康状态",
    "worker_pool_size": "Worker 池大小",
    "mesh_convergence_ms": "Mesh 收敛耗时",
}

TOKENS = {
    "http": "HTTP", "process": "进程", "cpu": "CPU", "func": "函数",
    "request": "请求", "requests": "请求", "req": "请求", "reqs": "请求",
    "response": "响应", "responses": "响应", "active": "活跃", "routing": "路由",
    "keys": "键", "key": "键", "seconds": "秒", "total": "累计",
    "latency": "延迟", "duration": "耗时", "prompt": "输入", "generation": "生成",
    "tokens": "Token", "token": "Token", "cached": "缓存", "uncached": "未缓存",
    "num": "数量", "count": "数量", "running": "运行中", "queue": "队列",
    "grammar": "Grammar", "throughput": "吞吐量", "cache": "缓存", "hit": "命中",
    "rate": "比率", "decode": "Decode", "prefill": "Prefill", "sum": "总和",
    "seq": "序列", "lens": "长度", "utilization": "利用率", "occupancy": "占用率",
    "cuda": "CUDA", "graph": "Graph", "kv": "KV", "swa": "SWA", "mamba": "Mamba",
    "available": "可用", "evictable": "可淘汰", "used": "已用", "realtime": "实时",
    "forward": "前向", "execution": "执行", "estimated": "估算", "flops": "FLOPs",
    "gpu": "GPU", "read": "读取", "write": "写入", "bytes": "字节",
    "engine": "引擎", "startup": "启动", "load": "加载", "weights": "权重",
    "page": "页", "pages": "页数", "size": "大小", "context": "上下文",
    "memory": "显存", "retracted": "回退", "aborted": "中止", "paused": "暂停",
    "stage": "阶段", "compilation": "编译", "schema": "Schema", "tree": "树",
    "traversal": "遍历", "avg": "平均", "max": "最大", "accept": "接受",
    "spec": "投机解码", "draft": "草稿", "wait": "等待", "outcomes": "结果",
    "bootstrap": "Bootstrap", "inflight": "处理中", "prealloc": "预分配",
    "pending": "待处理", "transfer": "传输", "speed": "速度", "failed": "失败",
    "retries": "重试", "retry": "重试", "eviction": "淘汰", "evicted": "已淘汰",
    "unique": "唯一", "all": "全部", "pool": "池", "slots": "槽位",
    "host": "主机", "streaming": "流式", "sessions": "会话", "held": "持有",
    "prefetched": "预取", "backuped": "备份", "bandwidth": "带宽",
    "physical": "物理", "balancedness": "均衡度", "recoveries": "恢复",
    "connections": "连接", "limit": "限流", "errors": "错误", "upstream": "上游",
    "worker": "Worker", "health": "健康", "checks": "检查", "selection": "选择",
    "manual": "手动", "policy": "策略", "branch": "分支", "consistent": "一致性",
    "hashing": "哈希", "prefix": "前缀", "state": "状态", "transitions": "转换",
    "consecutive": "连续", "failures": "失败", "successes": "成功", "exhausted": "耗尽",
    "backoff": "退避", "discovery": "服务发现", "registrations": "注册",
    "deregistrations": "注销", "sync": "同步", "discovered": "已发现",
    "tool": "工具", "calls": "调用", "servers": "服务", "iterations": "迭代",
    "operations": "操作", "items": "条目", "stored": "存储", "mesh": "Mesh",
    "convergence": "收敛", "batches": "批次", "snapshot": "快照", "trigger": "触发",
    "peer": "对端", "reconnects": "重连", "ack": "确认", "nack": "拒绝确认",
    "store": "存储", "cardinality": "基数", "hash": "哈希", "drift": "漂移",
    "ratio": "比率", "inflight": "处理中", "age": "时长", "generation": "生成",
}

TYPE_NAMES = {
    "counter": "Counter",
    "gauge": "Gauge",
    "histogram": "Histogram",
    "summary": "Summary",
}


def candidate_name(metric_name):
    short = metric_name.split(":", 1)[-1]
    for prefix in ("smg_", "router_"):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break
    if short in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[short]
    return " ".join(TOKENS.get(token, token.upper()) for token in short.split("_"))


def introduction(item, translated):
    metric_type = item["type"]
    if metric_type == "counter":
        return "累计统计{0}；看趋势时通常用 rate() 转换为每秒速率。".format(translated)
    if metric_type == "gauge":
        return "表示当前{0}，数值可随状态升降。".format(translated)
    if metric_type == "histogram":
        return "记录{0}的分布；看板提供 P80、P95 和平均值。".format(translated)
    return "记录{0}的分位数统计。".format(translated)


def metric_rows(groups, scope):
    rows = []
    for category, items in groups.items():
        translated_category = CATEGORY_TRANSLATIONS[category]
        for item in items:
            translated = candidate_name(item["name"])
            rows.append(
                "|  | `{0}` | {1} | {2} | {3} | {4} | {5} |".format(
                    item["name"], translated, TYPE_NAMES[item["type"]], scope,
                    translated_category, introduction(item, translated),
                )
            )
    return rows


def main():
    lines = [
        "# SGLang Dashboard 中文翻译候选清单",
        "",
        "本文用于评审 Grafana 界面中文化范围，当前 Dashboard JSON **尚未应用这些中文名**。在“选择”列标记需要采用或需要调整的项即可。指标名保持 Prometheus 原名，不做翻译。",
        "",
        "## 1. Dashboard 名称",
        "",
        "| 选择 | 当前名称 | 中文候选 | 角色范围 | 简介 |",
        "|---|---|---|---|---|",
    ]
    for current, translated, roles, intro in DASHBOARDS:
        lines.append("|  | {0} | {1} | {2} | {3} |".format(current, translated, roles, intro))

    lines.extend([
        "", "## 2. 分类名称", "",
        "| 选择 | 当前分类 | 中文候选 | 所属指标体系 |",
        "|---|---|---|---|",
    ])
    for category in ENGINE_GROUPS:
        lines.append("|  | {0} | {1} | Engine |".format(category, CATEGORY_TRANSLATIONS[category]))
    for category in ROUTER_GROUPS:
        lines.append("|  | {0} | {1} | Router |".format(category, CATEGORY_TRANSLATIONS[category]))

    lines.extend([
        "", "## 3. Engine 指标（PD 合部、Prefill、Decode 共用）", "",
        "共 122 个指标族。PD 合部和 PD 分离使用同一套 Collector，实际是否有样本取决于角色、功能开关和运行事件。",
        "", "| 选择 | Prometheus 指标名 | 中文候选 | 类型 | 角色范围 | 分类候选 | 简介 |",
        "|---|---|---|---|---|---|---|",
    ])
    lines.extend(metric_rows(ENGINE_GROUPS, "Unified / Prefill / Decode"))

    lines.extend([
        "", "## 4. Router 指标", "",
        "共 61 个指标族，包含 Router 本体和 Router Mesh。",
        "", "| 选择 | Prometheus 指标名 | 中文候选 | 类型 | 角色范围 | 分类候选 | 简介 |",
        "|---|---|---|---|---|---|---|",
    ])
    lines.extend(metric_rows(ROUTER_GROUPS, "Router"))
    lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
