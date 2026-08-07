# SGLang Dashboard 中文翻译候选清单

本文用于评审 Grafana 界面中文化范围，当前 Dashboard JSON **尚未应用这些中文名**。在“选择”列标记需要采用或需要调整的项即可。指标名保持 Prometheus 原名，不做翻译。

## 1. Dashboard 名称

| 选择 | 当前名称 | 中文候选 | 角色范围 | 简介 |
|---|---|---|---|---|
|  | SGLang PD Unified Metrics | SGLang PD 合部指标 | PD 合部 | 展示 unified engine 的 122 个指标族。 |
|  | SGLang PD Disaggregated and Router Metrics | SGLang PD 分离与 Router 指标 | Prefill / Decode / Router | 通过 Role 下拉框选择 Prefill、Decode 或 Router，共覆盖 183 个指标族。 |

## 2. 分类名称

| 选择 | 当前分类 | 中文候选 | 所属指标体系 |
|---|---|---|---|
|  | HTTP, Process and Functions | HTTP、进程与函数 | Engine |
|  | Requests, Tokens and User Latency | 请求、Token 与用户延迟 | Engine |
|  | Scheduler State | 调度器状态 | Engine |
|  | KV, SWA and Mamba Pools | KV、SWA 与 Mamba 资源池 | Engine |
|  | CUDA, Tokens and MFU Runtime | CUDA、Token 与 MFU 运行时 | Engine |
|  | Engine Capacity and Startup | 引擎容量与启动 | Engine |
|  | Retraction, Queue and Stage Latency | 回退、队列与阶段延迟 | Engine |
|  | Grammar | Grammar 结构化输出 | Engine |
|  | Speculative Decoding and Prefill Delayer | 投机解码与 Prefill 延迟器 | Engine |
|  | PD Queues and KV Transfer | PD 队列与 KV 传输 | Engine |
|  | Prefix Cache and Routing Keys | Prefix Cache 与路由键 | Engine |
|  | Optional LoRA, HiCache, Streaming and EPLB | 可选 LoRA、HiCache、流式会话与 EPLB | Engine |
|  | HTTP and Router Requests | HTTP 与 Router 请求 | Router |
|  | Worker Pool and Health | Worker 池与健康状态 | Router |
|  | Policies, Circuit Breaker and Retries | 路由策略、熔断与重试 | Router |
|  | Discovery, MCP and Persistence | 服务发现、MCP 与持久化 | Router |
|  | Router Mesh | Router Mesh 集群 | Router |

## 3. Engine 指标（PD 合部、Prefill、Decode 共用）

共 122 个指标族。PD 合部和 PD 分离使用同一套 Collector，实际是否有样本取决于角色、功能开关和运行事件。

| 选择 | Prometheus 指标名 | 中文候选 | 类型 | 角色范围 | 分类候选 | 简介 |
|---|---|---|---|---|---|---|
|  | `sglang:http_requests_total` | HTTP 请求 累计 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 累计统计HTTP 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:http_responses_total` | HTTP 响应 累计 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 累计统计HTTP 响应 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:http_requests_active` | HTTP 请求 活跃 | Gauge | Unified / Prefill / Decode | HTTP、进程与函数 | 表示当前HTTP 请求 活跃，数值可随状态升降。 |
|  | `sglang:routing_keys_active` | 路由 键 活跃 | Gauge | Unified / Prefill / Decode | HTTP、进程与函数 | 表示当前路由 键 活跃，数值可随状态升降。 |
|  | `sglang:process_cpu_seconds_total` | 进程 CPU 秒 累计 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 累计统计进程 CPU 秒 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:func_latency_seconds` | 函数 延迟 秒 | Histogram | Unified / Prefill / Decode | HTTP、进程与函数 | 记录函数 延迟 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:prompt_tokens_total` | 输入 Token 总数 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计输入 Token 总数；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:generation_tokens_total` | 生成 Token 总数 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计生成 Token 总数；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:spec_verify_calls_total` | 投机解码 VERIFY 调用 累计 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计投机解码 VERIFY 调用 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:prompt_tokens_histogram` | 输入 Token 数分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录输入 Token 数分布的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:uncached_prompt_tokens_histogram` | 未缓存输入 Token 数分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录未缓存输入 Token 数分布的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:generation_tokens_histogram` | 生成 Token 数分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录生成 Token 数分布的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:cached_tokens_total` | 缓存 Token 累计 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计缓存 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_requests_total` | 数量 请求 累计 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计数量 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:get_loads_duration_seconds` | GET LOADS 耗时 秒 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录GET LOADS 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:num_so_requests_total` | 数量 SO 请求 累计 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计数量 SO 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_aborted_requests_total` | 数量 中止 请求 累计 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计统计数量 中止 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:time_to_first_token_seconds` | 首 Token 延迟 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录首 Token 延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:inter_token_latency_seconds` | Token 间延迟（TPOT/ITL） | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录Token 间延迟（TPOT/ITL）的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:e2e_request_latency_seconds` | 请求端到端延迟 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 记录请求端到端延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:num_running_reqs` | 运行中请求数 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前运行中请求数，数值可随状态升降。 |
|  | `sglang:num_queue_reqs` | 排队请求数 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前排队请求数，数值可随状态升降。 |
|  | `sglang:num_grammar_queue_reqs` | 数量 Grammar 队列 请求 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前数量 Grammar 队列 请求，数值可随状态升降。 |
|  | `sglang:gen_throughput` | 生成吞吐量 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前生成吞吐量，数值可随状态升降。 |
|  | `sglang:cache_hit_rate` | 缓存命中率 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前缓存命中率，数值可随状态升降。 |
|  | `sglang:decode_sum_seq_lens` | Decode 总和 序列 长度 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前Decode 总和 序列 长度，数值可随状态升降。 |
|  | `sglang:utilization` | 利用率 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前利用率，数值可随状态升降。 |
|  | `sglang:fwd_occupancy` | FWD 占用率 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前FWD 占用率，数值可随状态升降。 |
|  | `sglang:new_token_ratio` | NEW Token 比率 | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前NEW Token 比率，数值可随状态升降。 |
|  | `sglang:is_cuda_graph` | IS CUDA Graph | Gauge | Unified / Prefill / Decode | 调度器状态 | 表示当前IS CUDA Graph，数值可随状态升降。 |
|  | `sglang:token_usage` | Token 池使用率 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前Token 池使用率，数值可随状态升降。 |
|  | `sglang:full_token_usage` | FULL Token USAGE | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前FULL Token USAGE，数值可随状态升降。 |
|  | `sglang:swa_token_usage` | SWA Token USAGE | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前SWA Token USAGE，数值可随状态升降。 |
|  | `sglang:mamba_usage` | Mamba USAGE | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前Mamba USAGE，数值可随状态升降。 |
|  | `sglang:num_used_tokens` | 数量 已用 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前数量 已用 Token，数值可随状态升降。 |
|  | `sglang:kv_available_tokens` | KV 可用 Token 数 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前KV 可用 Token 数，数值可随状态升降。 |
|  | `sglang:kv_evictable_tokens` | KV 可淘汰 Token 数 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前KV 可淘汰 Token 数，数值可随状态升降。 |
|  | `sglang:kv_used_tokens` | KV 已用 Token 数 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前KV 已用 Token 数，数值可随状态升降。 |
|  | `sglang:swa_available_tokens` | SWA 可用 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前SWA 可用 Token，数值可随状态升降。 |
|  | `sglang:swa_evictable_tokens` | SWA 可淘汰 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前SWA 可淘汰 Token，数值可随状态升降。 |
|  | `sglang:swa_used_tokens` | SWA 已用 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前SWA 已用 Token，数值可随状态升降。 |
|  | `sglang:mamba_available_tokens` | Mamba 可用 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前Mamba 可用 Token，数值可随状态升降。 |
|  | `sglang:mamba_evictable_tokens` | Mamba 可淘汰 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前Mamba 可淘汰 Token，数值可随状态升降。 |
|  | `sglang:mamba_used_tokens` | Mamba 已用 Token | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 表示当前Mamba 已用 Token，数值可随状态升降。 |
|  | `sglang:cuda_graph_passes_total` | CUDA Graph PASSES 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计CUDA Graph PASSES 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:realtime_tokens_total` | 实时 Token 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计实时 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:forward_execution_seconds_total` | 前向 执行 秒 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计前向 执行 秒 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:estimated_flops_per_gpu_total` | 估算 FLOPs PER GPU 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计估算 FLOPs PER GPU 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:estimated_read_bytes_per_gpu_total` | 估算 读取 字节 PER GPU 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计估算 读取 字节 PER GPU 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:estimated_write_bytes_per_gpu_total` | 估算 写入 字节 PER GPU 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计估算 写入 字节 PER GPU 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:dp_cooperation_realtime_tokens_total` | DP COOPERATION 实时 Token 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计DP COOPERATION 实时 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:dp_cooperation_forward_execution_seconds_total` | DP COOPERATION 前向 执行 秒 累计 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 累计统计DP COOPERATION 前向 执行 秒 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:max_total_num_tokens` | 最大 累计 数量 Token | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前最大 累计 数量 Token，数值可随状态升降。 |
|  | `sglang:max_running_requests_under_SLO` | 最大 运行中 请求 UNDER SLO | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前最大 运行中 请求 UNDER SLO，数值可随状态升降。 |
|  | `sglang:engine_startup_time` | 引擎启动耗时 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前引擎启动耗时，数值可随状态升降。 |
|  | `sglang:engine_load_weights_time` | 引擎权重加载耗时 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前引擎权重加载耗时，数值可随状态升降。 |
|  | `sglang:page_size` | 页 大小 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前页 大小，数值可随状态升降。 |
|  | `sglang:num_pages` | 数量 页数 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前数量 页数，数值可随状态升降。 |
|  | `sglang:context_len` | 上下文 LEN | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前上下文 LEN，数值可随状态升降。 |
|  | `sglang:startup_available_gpu_memory_gb` | 启动时可用 GPU 显存 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前启动时可用 GPU 显存，数值可随状态升降。 |
|  | `sglang:weight_load_duration_seconds` | WEIGHT 加载 耗时 秒 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 表示当前WEIGHT 加载 耗时 秒，数值可随状态升降。 |
|  | `sglang:num_retracted_reqs` | 数量 回退 请求 | Gauge | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 表示当前数量 回退 请求，数值可随状态升降。 |
|  | `sglang:num_retracted_requests_total` | 数量 回退 请求 累计 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计统计数量 回退 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_retracted_input_tokens_total` | 数量 回退 INPUT Token 累计 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计统计数量 回退 INPUT Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_retracted_output_tokens_total` | 数量 回退 OUTPUT Token 累计 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计统计数量 回退 OUTPUT Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_paused_reqs` | 数量 暂停 请求 | Gauge | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 表示当前数量 暂停 请求，数值可随状态升降。 |
|  | `sglang:queue_time_seconds` | 请求排队耗时 | Histogram | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 记录请求排队耗时的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:per_stage_req_latency_seconds` | 请求各阶段延迟 | Histogram | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 记录请求各阶段延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:grammar_compilation_time_seconds` | Grammar 编译 TIME 秒 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 记录Grammar 编译 TIME 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:num_grammar_cache_hit_total` | 数量 Grammar 缓存 命中 累计 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计统计数量 Grammar 缓存 命中 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_grammar_aborted_total` | 数量 Grammar 中止 累计 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计统计数量 Grammar 中止 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_grammar_timeout_total` | 数量 Grammar TIMEOUT 累计 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计统计数量 Grammar TIMEOUT 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_grammar_total` | 数量 Grammar 累计 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计统计数量 Grammar 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:grammar_schema_count` | Grammar Schema 数量 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 记录Grammar Schema 数量的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:grammar_ebnf_size` | Grammar EBNF 大小 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 记录Grammar EBNF 大小的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:grammar_tree_traversal_time_avg` | Grammar 树 遍历 TIME 平均 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 记录Grammar 树 遍历 TIME 平均的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:grammar_tree_traversal_time_max` | Grammar 树 遍历 TIME 最大 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 记录Grammar 树 遍历 TIME 最大的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:spec_accept_length` | 投机解码 接受 LENGTH | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 接受 LENGTH，数值可随状态升降。 |
|  | `sglang:spec_accept_rate` | 投机解码 接受 比率 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 接受 比率，数值可随状态升降。 |
|  | `sglang:spec_cap_length` | 投机解码 CAP LENGTH | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 CAP LENGTH，数值可随状态升降。 |
|  | `sglang:spec_block_accept_length` | 投机解码 BLOCK 接受 LENGTH | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 BLOCK 接受 LENGTH，数值可随状态升降。 |
|  | `sglang:spec_num_steps` | 投机解码 数量 STEPS | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 数量 STEPS，数值可随状态升降。 |
|  | `sglang:spec_num_draft_tokens` | 投机解码 数量 草稿 Token | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 表示当前投机解码 数量 草稿 Token，数值可随状态升降。 |
|  | `sglang:prefill_delayer_wait_forward_passes` | Prefill DELAYER 等待 前向 PASSES | Histogram | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 记录Prefill DELAYER 等待 前向 PASSES的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:prefill_delayer_wait_seconds` | Prefill DELAYER 等待 秒 | Histogram | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 记录Prefill DELAYER 等待 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:prefill_delayer_outcomes_total` | Prefill DELAYER 结果 累计 | Counter | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 累计统计Prefill DELAYER 结果 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_prefill_bootstrap_queue_reqs` | 数量 Prefill Bootstrap 队列 请求 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 表示当前数量 Prefill Bootstrap 队列 请求，数值可随状态升降。 |
|  | `sglang:num_prefill_inflight_queue_reqs` | 数量 Prefill 处理中 队列 请求 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 表示当前数量 Prefill 处理中 队列 请求，数值可随状态升降。 |
|  | `sglang:num_decode_prealloc_queue_reqs` | 数量 Decode 预分配 队列 请求 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 表示当前数量 Decode 预分配 队列 请求，数值可随状态升降。 |
|  | `sglang:num_decode_transfer_queue_reqs` | 数量 Decode 传输 队列 请求 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 表示当前数量 Decode 传输 队列 请求，数值可随状态升降。 |
|  | `sglang:pending_prealloc_token_usage` | 待处理 预分配 Token USAGE | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 表示当前待处理 预分配 Token USAGE，数值可随状态升降。 |
|  | `sglang:kv_transfer_speed_gb_s` | KV 传输速度 | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 记录KV 传输速度的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:kv_transfer_latency_ms` | KV 传输延迟 | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 记录KV 传输延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:kv_transfer_total_mb` | KV 传输数据量 | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 记录KV 传输数据量的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:kv_transfer_bootstrap_ms` | KV 传输 Bootstrap MS | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 记录KV 传输 Bootstrap MS的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:kv_transfer_alloc_ms` | KV 传输 ALLOC MS | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 记录KV 传输 ALLOC MS的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:num_bootstrap_failed_reqs_total` | 数量 Bootstrap 失败 请求 累计 | Counter | Unified / Prefill / Decode | PD 队列与 KV 传输 | 累计统计数量 Bootstrap 失败 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_transfer_failed_reqs_total` | 数量 传输 失败 请求 累计 | Counter | Unified / Prefill / Decode | PD 队列与 KV 传输 | 累计统计数量 传输 失败 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_prefill_retries_total` | 数量 Prefill 重试 累计 | Counter | Unified / Prefill / Decode | PD 队列与 KV 传输 | 累计统计数量 Prefill 重试 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:eviction_duration_seconds` | 淘汰 耗时 秒 | Histogram | Unified / Prefill / Decode | Prefix Cache 与路由键 | 记录淘汰 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:evicted_tokens_total` | 已淘汰 Token 累计 | Counter | Unified / Prefill / Decode | Prefix Cache 与路由键 | 累计统计已淘汰 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:load_back_duration_seconds` | 加载 BACK 耗时 秒 | Histogram | Unified / Prefill / Decode | Prefix Cache 与路由键 | 记录加载 BACK 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:load_back_tokens_total` | 加载 BACK Token 累计 | Counter | Unified / Prefill / Decode | Prefix Cache 与路由键 | 累计统计加载 BACK Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:num_unique_running_routing_keys` | 数量 唯一 运行中 路由 键 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 表示当前数量 唯一 运行中 路由 键，数值可随状态升降。 |
|  | `sglang:routing_key_running_req_count` | 路由 键 运行中 请求 数量 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 表示当前路由 键 运行中 请求 数量，数值可随状态升降。 |
|  | `sglang:routing_key_all_req_count` | 路由 键 全部 请求 数量 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 表示当前路由 键 全部 请求 数量，数值可随状态升降。 |
|  | `sglang:lora_pool_slots_used` | LORA 池 槽位 已用 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前LORA 池 槽位 已用，数值可随状态升降。 |
|  | `sglang:lora_pool_slots_total` | LORA 池 槽位 累计 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前LORA 池 槽位 累计，数值可随状态升降。 |
|  | `sglang:lora_pool_utilization` | LORA 池 利用率 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前LORA 池 利用率，数值可随状态升降。 |
|  | `sglang:hicache_host_used_tokens` | HICACHE 主机 已用 Token | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前HICACHE 主机 已用 Token，数值可随状态升降。 |
|  | `sglang:hicache_host_total_tokens` | HICACHE 主机 累计 Token | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前HICACHE 主机 累计 Token，数值可随状态升降。 |
|  | `sglang:num_streaming_sessions` | 数量 流式 会话 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前数量 流式 会话，数值可随状态升降。 |
|  | `sglang:streaming_session_held_tokens` | 流式 SESSION 持有 Token | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 表示当前流式 SESSION 持有 Token，数值可随状态升降。 |
|  | `sglang:prefetched_tokens_total` | 预取 Token 累计 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计统计预取 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:backuped_tokens_total` | 备份 Token 累计 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计统计备份 Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `sglang:prefetch_pgs` | PREFETCH PGS | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录PREFETCH PGS的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:backup_pgs` | BACKUP PGS | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录BACKUP PGS的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:prefetch_bandwidth` | PREFETCH 带宽 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录PREFETCH 带宽的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:backup_bandwidth` | BACKUP 带宽 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录BACKUP 带宽的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:eplb_gpu_physical_count` | EPLB GPU 物理 数量 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录EPLB GPU 物理 数量的分布；看板提供 P80、P95 和平均值。 |
|  | `sglang:eplb_balancedness` | EPLB 均衡度 | Summary | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 记录EPLB 均衡度的分位数统计。 |
|  | `sglang:failed_session_recoveries_total` | 失败 SESSION 恢复 累计 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计统计失败 SESSION 恢复 累计；看趋势时通常用 rate() 转换为每秒速率。 |

## 4. Router 指标

共 61 个指标族，包含 Router 本体和 Router Mesh。

| 选择 | Prometheus 指标名 | 中文候选 | 类型 | 角色范围 | 分类候选 | 简介 |
|---|---|---|---|---|---|---|
|  | `smg_http_requests_total` | HTTP 请求 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计HTTP 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_http_request_duration_seconds` | HTTP 请求 耗时 秒 | Histogram | Router | HTTP 与 Router 请求 | 记录HTTP 请求 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_http_inflight_request_age_count` | HTTP 处理中 请求 时长 数量 | Gauge | Router | HTTP 与 Router 请求 | 表示当前HTTP 处理中 请求 时长 数量，数值可随状态升降。 |
|  | `smg_http_responses_total` | HTTP 响应 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计HTTP 响应 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_http_connections_active` | HTTP 连接 活跃 | Gauge | Router | HTTP 与 Router 请求 | 表示当前HTTP 连接 活跃，数值可随状态升降。 |
|  | `smg_http_rate_limit_total` | HTTP 比率 限流 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计HTTP 比率 限流 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_router_requests_total` | ROUTER 请求 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计ROUTER 请求 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_router_request_duration_seconds` | Router 请求耗时 | Histogram | Router | HTTP 与 Router 请求 | 记录Router 请求耗时的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_router_request_errors_total` | ROUTER 请求 错误 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计ROUTER 请求 错误 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_router_stage_duration_seconds` | ROUTER 阶段 耗时 秒 | Histogram | Router | HTTP 与 Router 请求 | 记录ROUTER 阶段 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_router_upstream_responses_total` | ROUTER 上游 响应 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计ROUTER 上游 响应 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_router_ttft_seconds` | Router 首 Token 延迟 | Histogram | Router | HTTP 与 Router 请求 | 记录Router 首 Token 延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_router_tpot_seconds` | Router Token 间延迟 | Histogram | Router | HTTP 与 Router 请求 | 记录Router Token 间延迟的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_router_tokens_total` | ROUTER Token 累计 | Counter | Router | HTTP 与 Router 请求 | 累计统计ROUTER Token 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_router_generation_duration_seconds` | ROUTER 生成 耗时 秒 | Histogram | Router | HTTP 与 Router 请求 | 记录ROUTER 生成 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_worker_pool_size` | Worker 池大小 | Gauge | Router | Worker 池与健康状态 | 表示当前Worker 池大小，数值可随状态升降。 |
|  | `smg_worker_connections_active` | Worker 连接 活跃 | Gauge | Router | Worker 池与健康状态 | 表示当前Worker 连接 活跃，数值可随状态升降。 |
|  | `smg_worker_requests_active` | Worker 请求 活跃 | Gauge | Router | Worker 池与健康状态 | 表示当前Worker 请求 活跃，数值可随状态升降。 |
|  | `smg_worker_health` | Worker 健康状态 | Gauge | Router | Worker 池与健康状态 | 表示当前Worker 健康状态，数值可随状态升降。 |
|  | `smg_worker_health_checks_total` | Worker 健康 检查 累计 | Counter | Router | Worker 池与健康状态 | 累计统计Worker 健康 检查 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_selection_total` | Worker 选择 累计 | Counter | Router | Worker 池与健康状态 | 累计统计Worker 选择 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_errors_total` | Worker 错误 累计 | Counter | Router | Worker 池与健康状态 | 累计统计Worker 错误 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_routing_keys_active` | Worker 路由 键 活跃 | Gauge | Router | Worker 池与健康状态 | 表示当前Worker 路由 键 活跃，数值可随状态升降。 |
|  | `smg_manual_policy_cache_entries` | 手动 策略 缓存 ENTRIES | Gauge | Router | 路由策略、熔断与重试 | 表示当前手动 策略 缓存 ENTRIES，数值可随状态升降。 |
|  | `smg_manual_policy_branch_total` | 手动 策略 分支 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计手动 策略 分支 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_consistent_hashing_policy_branch_total` | 一致性 哈希 策略 分支 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计一致性 哈希 策略 分支 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_prefix_hash_policy_branch_total` | 前缀 哈希 策略 分支 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计前缀 哈希 策略 分支 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_cb_state` | Worker CB 状态 | Gauge | Router | 路由策略、熔断与重试 | 表示当前Worker CB 状态，数值可随状态升降。 |
|  | `smg_worker_cb_transitions_total` | Worker CB 转换 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计Worker CB 转换 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_cb_outcomes_total` | Worker CB 结果 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计Worker CB 结果 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_cb_consecutive_failures` | Worker CB 连续 失败 | Gauge | Router | 路由策略、熔断与重试 | 表示当前Worker CB 连续 失败，数值可随状态升降。 |
|  | `smg_worker_cb_consecutive_successes` | Worker CB 连续 成功 | Gauge | Router | 路由策略、熔断与重试 | 表示当前Worker CB 连续 成功，数值可随状态升降。 |
|  | `smg_worker_retries_total` | Worker 重试 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计Worker 重试 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_retries_exhausted_total` | Worker 重试 耗尽 累计 | Counter | Router | 路由策略、熔断与重试 | 累计统计Worker 重试 耗尽 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_worker_retry_backoff_seconds` | Worker 重试 退避 秒 | Histogram | Router | 路由策略、熔断与重试 | 记录Worker 重试 退避 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_discovery_registrations_total` | 服务发现 注册 累计 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计服务发现 注册 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_discovery_deregistrations_total` | 服务发现 注销 累计 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计服务发现 注销 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_discovery_sync_duration_seconds` | 服务发现 同步 耗时 秒 | Histogram | Router | 服务发现、MCP 与持久化 | 记录服务发现 同步 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_discovery_workers_discovered` | 服务发现 WORKERS 已发现 | Gauge | Router | 服务发现、MCP 与持久化 | 表示当前服务发现 WORKERS 已发现，数值可随状态升降。 |
|  | `smg_mcp_tool_calls_total` | MCP 工具 调用 累计 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计MCP 工具 调用 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_mcp_tool_duration_seconds` | MCP 工具 耗时 秒 | Histogram | Router | 服务发现、MCP 与持久化 | 记录MCP 工具 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_mcp_servers_active` | MCP 服务 活跃 | Gauge | Router | 服务发现、MCP 与持久化 | 表示当前MCP 服务 活跃，数值可随状态升降。 |
|  | `smg_mcp_tool_iterations_total` | MCP 工具 迭代 累计 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计MCP 工具 迭代 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_db_operations_total` | DB 操作 累计 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计DB 操作 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `smg_db_operation_duration_seconds` | DB OPERATION 耗时 秒 | Histogram | Router | 服务发现、MCP 与持久化 | 记录DB OPERATION 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `smg_db_connections_active` | DB 连接 活跃 | Gauge | Router | 服务发现、MCP 与持久化 | 表示当前DB 连接 活跃，数值可随状态升降。 |
|  | `smg_db_items_stored` | DB 条目 存储 | Counter | Router | 服务发现、MCP 与持久化 | 累计统计DB 条目 存储；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_convergence_ms` | Mesh 收敛耗时 | Histogram | Router | Router Mesh 集群 | 记录Mesh 收敛耗时的分布；看板提供 P80、P95 和平均值。 |
|  | `router_mesh_batches_total` | Mesh 批次 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 批次 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_bytes_total` | Mesh 字节 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 字节 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_snapshot_trigger_total` | Mesh 快照 触发 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 快照 触发 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_snapshot_duration_seconds` | Mesh 快照 耗时 秒 | Histogram | Router | Router Mesh 集群 | 记录Mesh 快照 耗时 秒的分布；看板提供 P80、P95 和平均值。 |
|  | `router_mesh_snapshot_bytes_total` | Mesh 快照 字节 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 快照 字节 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_peer_connections` | Mesh 对端 连接 | Gauge | Router | Router Mesh 集群 | 表示当前Mesh 对端 连接，数值可随状态升降。 |
|  | `router_mesh_peer_reconnects_total` | Mesh 对端 重连 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 对端 重连 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_peer_ack_total` | Mesh 对端 确认 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 对端 确认 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_peer_nack_total` | Mesh 对端 拒绝确认 累计 | Counter | Router | Router Mesh 集群 | 累计统计Mesh 对端 拒绝确认 累计；看趋势时通常用 rate() 转换为每秒速率。 |
|  | `router_mesh_store_cardinality` | Mesh 存储 基数 | Gauge | Router | Router Mesh 集群 | 表示当前Mesh 存储 基数，数值可随状态升降。 |
|  | `router_mesh_store_hash` | Mesh 存储 哈希 | Gauge | Router | Router Mesh 集群 | 表示当前Mesh 存储 哈希，数值可随状态升降。 |
|  | `router_rl_drift_ratio` | RL 漂移 比率 | Gauge | Router | Router Mesh 集群 | 表示当前RL 漂移 比率，数值可随状态升降。 |
|  | `router_lb_drift_ratio` | LB 漂移 比率 | Gauge | Router | Router Mesh 集群 | 表示当前LB 漂移 比率，数值可随状态升降。 |
