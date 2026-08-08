# SGLang Dashboard 中文翻译候选清单

本文是 Grafana 中文界面使用的翻译目录评审视图。Prometheus 原始指标标识保持不变；Gauge/Histogram 面板标题使用“中文名称（大致解释）”，Counter 趋势面板根据 rate() 查询使用速率名称。原始指标名、累计语义及完整映射保留在面板信息和本清单中。

## 1. Dashboard 名称

| 选择 | 当前名称 | 中文候选 | 角色范围 | 简介 |
|---|---|---|---|---|
|  | SGLang PD Unified Metrics | SGLang PD 合部指标 | PD 合部 | 展示 unified engine 的 122 个指标族。 |
|  | SGLang PD Disaggregated and Router Metrics | SGLang PD 分离与 Router 指标 | Prefill / Decode / Router | 通过 Role 下拉框单选、多选或选择 All 查看 Prefill、Decode 和 Router，共覆盖 183 个指标族。 |

## 2. 分类名称

| 选择 | 当前分类 | 中文候选 | 所属指标体系 |
|---|---|---|---|
|  | Key Engine Metrics | 关键引擎指标 | Engine |
|  | Request Latency Pipeline | 请求全链路时延 | Engine |
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
|  | Key Router Metrics | 关键 Router 指标 | Router |
|  | Router Request Latency Pipeline | Router 请求全链路时延 | Router |
|  | HTTP and Router Requests | HTTP 与 Router 请求 | Router |
|  | Worker Pool and Health | Worker 池与健康状态 | Router |
|  | Policies, Circuit Breaker and Retries | 路由策略、熔断与重试 | Router |
|  | Discovery, MCP and Persistence | 服务发现、MCP 与持久化 | Router |
|  | Router Mesh | Router Mesh 集群 | Router |

## 3. Engine 指标（PD 合部、Prefill、Decode 共用）

共 122 个指标族。PD 合部和 PD 分离使用同一套 Collector，实际是否有样本取决于角色、功能开关和运行事件。

| 选择 | Prometheus 指标名 | 指标名称中文翻译候选 | 类型 | 角色范围 | 分类候选 | 简介 |
|---|---|---|---|---|---|---|
|  | `sglang:num_requests_total` | 已处理请求总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计处理完成的推理请求数。 |
|  | `sglang:prompt_tokens_total` | Prefill Token 总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计处理的输入（Prefill）Token 数。 |
|  | `sglang:generation_tokens_total` | 生成 Token 总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计处理的生成 Token 数。 |
|  | `sglang:num_aborted_requests_total` | 中止请求总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计被中止的请求数。 |
|  | `sglang:num_running_reqs` | 运行中请求数 | Gauge | Unified / Prefill / Decode | 关键引擎指标 | 调度器当前正在运行的请求数。 |
|  | `sglang:num_queue_reqs` | 等待队列请求数 | Gauge | Unified / Prefill / Decode | 关键引擎指标 | 调度器普通等待队列中的请求数。 |
|  | `sglang:token_usage` | Token 池使用率 | Gauge | Unified / Prefill / Decode | 关键引擎指标 | Token 内存池的总体使用率。 |
|  | `sglang:utilization` | 引擎利用率 | Gauge | Unified / Prefill / Decode | 关键引擎指标 | 调度器计算得到的当前引擎利用率。 |
|  | `sglang:time_to_first_token_seconds` | 首 Token 延迟（TTFT） | Histogram | Unified / Prefill / Decode | 关键引擎指标 | 从请求进入到生成首个 Token 的耗时分布，单位为秒。 |
|  | `sglang:inter_token_latency_seconds` | Token 间延迟（ITL） | Histogram | Unified / Prefill / Decode | 关键引擎指标 | 相邻输出 Token 之间的耗时分布，单位为秒。 |
|  | `sglang:e2e_request_latency_seconds` | 请求端到端延迟 | Histogram | Unified / Prefill / Decode | 关键引擎指标 | 请求从进入服务到完成的端到端耗时分布，单位为秒。 |
|  | `sglang:kv_transfer_latency_ms` | KV Cache 传输延迟 | Histogram | Unified / Prefill / Decode | 关键引擎指标 | KV Cache 传输耗时分布，单位为毫秒。 |
|  | `sglang:num_transfer_failed_reqs_total` | KV 传输失败请求总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计 KV Cache 传输失败的请求数。 |
|  | `sglang:num_bootstrap_failed_reqs_total` | Bootstrap 失败请求总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计 Bootstrap 失败的请求数。 |
|  | `sglang:num_prefill_retries_total` | Prefill 重试总数 | Counter | Unified / Prefill / Decode | 关键引擎指标 | 累计执行的 Prefill 重试次数。 |
|  | `sglang:queue_time_seconds` | 请求排队耗时 | Histogram | Unified / Prefill / Decode | 请求全链路时延 | 请求在调度队列中等待的时间分布，单位为秒。 |
|  | `sglang:prefill_delayer_wait_seconds` | Prefill 延迟器等待耗时 | Histogram | Unified / Prefill / Decode | 请求全链路时延 | Prefill 延迟器的等待时间分布，单位为秒。 |
|  | `sglang:kv_transfer_bootstrap_ms` | KV 传输 Bootstrap 耗时 | Histogram | Unified / Prefill / Decode | 请求全链路时延 | KV 传输 Bootstrap 阶段耗时分布，单位为毫秒。 |
|  | `sglang:kv_transfer_alloc_ms` | KV 传输分配等待耗时 | Histogram | Unified / Prefill / Decode | 请求全链路时延 | KV 传输等待内存分配的耗时分布，单位为毫秒。 |
|  | `sglang:per_stage_req_latency_seconds` | 请求阶段耗时 | Histogram | Unified / Prefill / Decode | 请求全链路时延 | 请求各处理阶段的耗时分布，按 stage 标签区分，单位为秒。 |
|  | `sglang:http_requests_total` | HTTP 请求总数 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 按接口和方法累计收到的 HTTP 请求数。 |
|  | `sglang:http_responses_total` | HTTP 响应总数 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 按接口、方法和状态码累计返回的 HTTP 响应数。 |
|  | `sglang:http_requests_active` | 活跃 HTTP 请求数 | Gauge | Unified / Prefill / Decode | HTTP、进程与函数 | 当前正在处理的 HTTP 请求数，按接口和方法区分。 |
|  | `sglang:routing_keys_active` | 活跃路由键数 | Gauge | Unified / Prefill / Decode | HTTP、进程与函数 | 当前存在活跃请求的唯一路由键数量。 |
|  | `sglang:process_cpu_seconds_total` | 进程 CPU 时间 | Counter | Unified / Prefill / Decode | HTTP、进程与函数 | 各组件进程累计消耗的用户态与内核态 CPU 时间，单位为秒。 |
|  | `sglang:func_latency_seconds` | 函数执行耗时 | Histogram | Unified / Prefill / Decode | HTTP、进程与函数 | 被监控函数的执行耗时分布，单位为秒，按函数名区分。 |
|  | `sglang:spec_verify_calls_total` | 投机解码验证调用总数 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计执行的投机解码验证调用次数。 |
|  | `sglang:prompt_tokens_histogram` | 输入 Token 长度分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 每个请求的输入 Token 数量分布。 |
|  | `sglang:uncached_prompt_tokens_histogram` | 未缓存输入 Token 长度分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 每个请求实际需要计算、未由缓存命中的输入 Token 数量分布。 |
|  | `sglang:generation_tokens_histogram` | 生成 Token 长度分布 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 每个请求的生成 Token 数量分布。 |
|  | `sglang:cached_tokens_total` | 缓存命中 Token 总数 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计由设备、主机或存储缓存命中的输入 Token 数，按 cache_source 区分来源。 |
|  | `sglang:get_loads_duration_seconds` | 负载查询耗时 | Histogram | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 处理 /v1/loads 请求所花费的时间分布，单位为秒。 |
|  | `sglang:num_so_requests_total` | 结构化输出请求总数 | Counter | Unified / Prefill / Decode | 请求、Token 与用户延迟 | 累计处理的结构化输出请求数。 |
|  | `sglang:num_grammar_queue_reqs` | Grammar 等待队列请求数 | Gauge | Unified / Prefill / Decode | 调度器状态 | 等待 Grammar 处理的请求数。 |
|  | `sglang:gen_throughput` | 生成吞吐量 | Gauge | Unified / Prefill / Decode | 调度器状态 | 当前生成吞吐量，单位为 Token/s。 |
|  | `sglang:cache_hit_rate` | 前缀缓存命中率 | Gauge | Unified / Prefill / Decode | 调度器状态 | Prefix Cache 的命中率。 |
|  | `sglang:decode_sum_seq_lens` | Decode 序列总长度 | Gauge | Unified / Prefill / Decode | 调度器状态 | 当前 Decode 批次中所有序列长度之和。 |
|  | `sglang:fwd_occupancy` | 前向计算 GPU 占用率 | Gauge | Unified / Prefill / Decode | 调度器状态 | 前向计算期间的 GPU 占用百分比。 |
|  | `sglang:new_token_ratio` | 新 Token 比例 | Gauge | Unified / Prefill / Decode | 调度器状态 | 调度器当前使用的新 Token 比例。 |
|  | `sglang:is_cuda_graph` | CUDA Graph 使用状态 | Gauge | Unified / Prefill / Decode | 调度器状态 | 当前批次是否使用 CUDA Graph；使用为 1，否则为 0。 |
|  | `sglang:full_token_usage` | 全注意力 Token 池使用率 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | Full Attention 层 Token 内存池的使用率。 |
|  | `sglang:swa_token_usage` | SWA Token 池使用率 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 滑动窗口注意力（SWA）层 Token 内存池的使用率。 |
|  | `sglang:mamba_usage` | Mamba 状态池使用率 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | Mamba/SSM 状态内存池的使用率。 |
|  | `sglang:num_used_tokens` | 已用 Token 数 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | Token 内存池中已使用的 Token 数。 |
|  | `sglang:kv_available_tokens` | KV Cache 可用 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | KV Cache 池中空闲的 Token 槽位数。 |
|  | `sglang:kv_evictable_tokens` | KV Cache 可淘汰 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | KV Cache 池中可从 Radix Cache 淘汰的 Token 槽位数。 |
|  | `sglang:kv_used_tokens` | KV Cache 活跃 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | KV Cache 池中被活跃请求占用的 Token 槽位数。 |
|  | `sglang:swa_available_tokens` | SWA 可用 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 混合 SWA 模型的 SWA 池中空闲 Token 槽位数。 |
|  | `sglang:swa_evictable_tokens` | SWA 可淘汰 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | SWA 池中可从 Radix Cache 淘汰的 Token 槽位数。 |
|  | `sglang:swa_used_tokens` | SWA 活跃 Token 槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | SWA 池中被活跃请求占用的 Token 槽位数。 |
|  | `sglang:mamba_available_tokens` | Mamba 可用状态槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | 混合 SSM 模型的 Mamba 状态池中空闲槽位数。 |
|  | `sglang:mamba_evictable_tokens` | Mamba 可淘汰状态槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | Mamba 状态池中可从 Radix Cache 淘汰的状态槽位数。 |
|  | `sglang:mamba_used_tokens` | Mamba 活跃状态槽位 | Gauge | Unified / Prefill / Decode | KV、SWA 与 Mamba 资源池 | Mamba 状态池中被活跃请求占用的状态槽位数。 |
|  | `sglang:cuda_graph_passes_total` | CUDA Graph 前向次数 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 按执行模式累计前向计算次数，用于区分 CUDA Graph 与普通执行。 |
|  | `sglang:realtime_tokens_total` | 实时处理 Token 总数 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 按日志周期累计处理的 Token 数，区分 Prefill 计算、Prefill 缓存命中和 Decode。 |
|  | `sglang:forward_execution_seconds_total` | 前向计算累计耗时 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 按 Prefill、Decode 等类别累计前向计算耗时，单位为秒。 |
|  | `sglang:estimated_flops_per_gpu_total` | 单 GPU 估算 FLOPs 总量 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 每个 GPU 累计估算的浮点运算量，用于计算模型 FLOPs 利用率（MFU）。 |
|  | `sglang:estimated_read_bytes_per_gpu_total` | 单 GPU 估算显存读取量 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 每个 GPU 累计估算的显存读取字节数，用于估算内存带宽利用情况。 |
|  | `sglang:estimated_write_bytes_per_gpu_total` | 单 GPU 估算显存写入量 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 每个 GPU 累计估算的显存写入字节数，用于估算内存带宽利用情况。 |
|  | `sglang:dp_cooperation_realtime_tokens_total` | DP 协同处理 Token 总数 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 按 Prefill rank 数和处理模式累计 DP Attention 协同处理的 Token 数。 |
|  | `sglang:dp_cooperation_forward_execution_seconds_total` | DP 协同前向累计耗时 | Counter | Unified / Prefill / Decode | CUDA、Token 与 MFU 运行时 | 按 Prefill rank 数和执行类别累计 DP Attention 协同前向耗时，单位为秒。 |
|  | `sglang:max_total_num_tokens` | KV Cache 最大 Token 容量 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | KV Cache 池可容纳的最大 Token 总数。 |
|  | `sglang:max_running_requests_under_SLO` | SLO 下最大并发请求数 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 在目标 SLO 约束下估算的最大运行中请求数。 |
|  | `sglang:engine_startup_time` | 引擎启动耗时 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 引擎完成启动所花费的时间。 |
|  | `sglang:engine_load_weights_time` | 引擎权重加载耗时 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 引擎启动期间加载模型权重所花费的时间。 |
|  | `sglang:page_size` | KV Cache 页大小 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 每个 KV Cache 页包含的 Token 数。 |
|  | `sglang:num_pages` | KV Cache 页数 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | KV Cache 中的页面总数。 |
|  | `sglang:context_len` | 最大上下文长度 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 模型支持的最大上下文长度，单位为 Token。 |
|  | `sglang:startup_available_gpu_memory_gb` | 启动时可用 GPU 显存 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 引擎启动时检测到的可用 GPU 显存，单位为 GB。 |
|  | `sglang:weight_load_duration_seconds` | 最近一次在线权重加载耗时 | Gauge | Unified / Prefill / Decode | 引擎容量与启动 | 最近一次在线更新权重操作的墙钟耗时，单位为秒，按加载来源区分。 |
|  | `sglang:num_retracted_reqs` | 本周期回退请求数 | Gauge | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 当前统计周期内因资源不足等原因被调度器回退的请求数。 |
|  | `sglang:num_retracted_requests_total` | 回退请求总数 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计被调度器回退的请求数。 |
|  | `sglang:num_retracted_input_tokens_total` | 回退输入 Token 总数 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计随请求回退的输入 Token 数。 |
|  | `sglang:num_retracted_output_tokens_total` | 回退输出 Token 总数 | Counter | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 累计随请求回退的输出 Token 数。 |
|  | `sglang:num_paused_reqs` | 暂停请求数 | Gauge | Unified / Prefill / Decode | 回退、队列与阶段延迟 | 因异步权重同步而暂停的请求数。 |
|  | `sglang:grammar_compilation_time_seconds` | Grammar 编译耗时 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | Grammar 编译耗时分布，单位为秒。 |
|  | `sglang:num_grammar_cache_hit_total` | Grammar 缓存命中总数 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计命中 Grammar 缓存的次数。 |
|  | `sglang:num_grammar_aborted_total` | Grammar 中止请求总数 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计因 Grammar 处理而中止的请求数。 |
|  | `sglang:num_grammar_timeout_total` | Grammar 超时总数 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计发生的 Grammar 超时次数。 |
|  | `sglang:num_grammar_total` | Grammar 请求总数 | Counter | Unified / Prefill / Decode | Grammar 结构化输出 | 累计处理的 Grammar 约束请求数。 |
|  | `sglang:grammar_schema_count` | Grammar Schema 数量分布 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 单次 Grammar 处理涉及的 Schema 数量分布。 |
|  | `sglang:grammar_ebnf_size` | Grammar EBNF 大小分布 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | Grammar EBNF 定义大小的分布。 |
|  | `sglang:grammar_tree_traversal_time_avg` | Grammar 树平均遍历耗时 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 单次统计中 Grammar 树平均遍历耗时的分布，单位为秒。 |
|  | `sglang:grammar_tree_traversal_time_max` | Grammar 树最大遍历耗时 | Histogram | Unified / Prefill / Decode | Grammar 结构化输出 | 单次统计中 Grammar 树最大遍历耗时的分布，单位为秒。 |
|  | `sglang:spec_accept_length` | 投机解码平均接受长度 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 每次验证平均接受的长度，包括已接受草稿 Token 和奖励 Token。 |
|  | `sglang:spec_accept_rate` | 投机解码接受率 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 批次内已接受草稿 Token 数与提议草稿 Token 数之比。 |
|  | `sglang:spec_cap_length` | 投机解码验证窗口长度 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | DSpark 置信度调度下每次验证的平均窗口长度，包含奖励槽位。 |
|  | `sglang:spec_block_accept_length` | 投机解码整块接受长度 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 每次验证未受 cap 限制的完整块平均接受长度。 |
|  | `sglang:spec_num_steps` | 投机解码步数 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 当前启用的 speculative_num_steps 配置值。 |
|  | `sglang:spec_num_draft_tokens` | 投机解码草稿 Token 数 | Gauge | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 当前每轮投机解码使用的草稿 Token 数。 |
|  | `sglang:prefill_delayer_wait_forward_passes` | Prefill 延迟器等待前向次数 | Histogram | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | Prefill 延迟器在放行前等待的前向计算次数分布。 |
|  | `sglang:prefill_delayer_outcomes_total` | Prefill 延迟器结果总数 | Counter | Unified / Prefill / Decode | 投机解码与 Prefill 延迟器 | 按输入估算方式和是否放行累计 Prefill 延迟器的决策结果。 |
|  | `sglang:num_prefill_bootstrap_queue_reqs` | Prefill Bootstrap 队列请求数 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | Prefill 节点 Bootstrap 队列中的请求数。 |
|  | `sglang:num_prefill_inflight_queue_reqs` | Prefill 传输中请求数 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | Prefill 节点已进入处理或 KV 传输流程的请求数。 |
|  | `sglang:num_decode_prealloc_queue_reqs` | Decode 预分配队列请求数 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | Decode 节点等待 KV Cache 预分配的请求数。 |
|  | `sglang:num_decode_transfer_queue_reqs` | Decode 传输队列请求数 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | Decode 节点等待或进行 KV Cache 传输的请求数。 |
|  | `sglang:pending_prealloc_token_usage` | 待预分配 Token 使用量 | Gauge | Unified / Prefill / Decode | PD 队列与 KV 传输 | 尚未实际完成预分配的待处理 Token 使用量；源码未明确其量纲。 |
|  | `sglang:kv_transfer_speed_gb_s` | KV Cache 传输速度 | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | KV Cache 传输速度分布，单位为 GB/s。 |
|  | `sglang:kv_transfer_total_mb` | KV Cache 传输数据量 | Histogram | Unified / Prefill / Decode | PD 队列与 KV 传输 | 单次 KV Cache 传输数据量分布，单位为 MB。 |
|  | `sglang:eviction_duration_seconds` | KV Cache 淘汰耗时 | Histogram | Unified / Prefill / Decode | Prefix Cache 与路由键 | 将 KV Cache 从 GPU 淘汰到 CPU 的耗时分布，单位为秒。 |
|  | `sglang:evicted_tokens_total` | 淘汰 Token 总数 | Counter | Unified / Prefill / Decode | Prefix Cache 与路由键 | 累计从 GPU 淘汰到 CPU 的 Token 数。 |
|  | `sglang:load_back_duration_seconds` | KV Cache 回载耗时 | Histogram | Unified / Prefill / Decode | Prefix Cache 与路由键 | 将 KV Cache 从 CPU 回载到 GPU 的耗时分布，单位为秒。 |
|  | `sglang:load_back_tokens_total` | 回载 Token 总数 | Counter | Unified / Prefill / Decode | Prefix Cache 与路由键 | 累计从 CPU 回载到 GPU 的 Token 数。 |
|  | `sglang:num_unique_running_routing_keys` | 运行中唯一路由键数 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 当前运行批次中的唯一路由键数量。 |
|  | `sglang:routing_key_running_req_count` | 路由键运行请求数分布 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 按每个路由键关联的运行中请求数划分的非累积区间分布，区间由 gt 和 le 标识。 |
|  | `sglang:routing_key_all_req_count` | 路由键全部请求数分布 | Gauge | Unified / Prefill / Decode | Prefix Cache 与路由键 | 按每个路由键关联的运行中与等待请求总数划分的非累积区间分布。 |
|  | `sglang:lora_pool_slots_used` | LoRA 已用槽位数 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | GPU 内存中当前已占用的 LoRA Adapter 槽位数。 |
|  | `sglang:lora_pool_slots_total` | LoRA 槽位总数 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 可用的 LoRA Adapter 槽位总数，即 max_loras_per_batch。 |
|  | `sglang:lora_pool_utilization` | LoRA 槽位使用率 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | LoRA 已用槽位数与总槽位数之比，1 表示已满。 |
|  | `sglang:hicache_host_used_tokens` | HiCache 主机已用 Token 数 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 主机端 KV Cache 当前已使用的 Token 数。 |
|  | `sglang:hicache_host_total_tokens` | HiCache 主机 Token 容量 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 主机端 KV Cache 可容纳的 Token 总数。 |
|  | `sglang:num_streaming_sessions` | 流式会话数 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 当前流式会话数量。 |
|  | `sglang:streaming_session_held_tokens` | 流式会话持有 Token 数 | Gauge | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 流式会话槽位当前保留的 KV Token 数。 |
|  | `sglang:prefetched_tokens_total` | 预取 Token 总数 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计从分层存储预取的输入 Token 数。 |
|  | `sglang:backuped_tokens_total` | 备份 Token 总数 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计备份到分层存储的 Token 数。 |
|  | `sglang:prefetch_pgs` | 预取页数分布 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 每批次从分层存储预取的页面数量分布。 |
|  | `sglang:backup_pgs` | 备份页数分布 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 每批次备份到分层存储的页面数量分布。 |
|  | `sglang:prefetch_bandwidth` | 预取带宽 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 从分层存储预取数据的带宽分布，单位为 GB/s。 |
|  | `sglang:backup_bandwidth` | 备份带宽 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 向分层存储备份数据的带宽分布，单位为 GB/s。 |
|  | `sglang:eplb_gpu_physical_count` | EPLB 物理专家数分布 | Histogram | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 各层、各 GPU rank 被选中的物理专家数量分布。 |
|  | `sglang:eplb_balancedness` | EPLB 负载均衡度 | Summary | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 专家并行中 MoE 专家负载的均衡程度，按前向模式区分。 |
|  | `sglang:failed_session_recoveries_total` | Mooncake 会话恢复总数 | Counter | Unified / Prefill / Decode | 可选 LoRA、HiCache、流式会话与 EPLB | 累计通过探测从黑名单恢复的 Mooncake session_id 数。 |

## 4. Router 指标

共 61 个指标族，包含 Router 本体和 Router Mesh。

| 选择 | Prometheus 指标名 | 指标名称中文翻译候选 | 类型 | 角色范围 | 分类候选 | 简介 |
|---|---|---|---|---|---|---|
|  | `smg_http_requests_total` | Router HTTP 请求总数 | Counter | Router | 关键 Router 指标 | 按 HTTP 方法和路径累计 Router 收到的请求数。 |
|  | `smg_http_responses_total` | Router HTTP 响应总数 | Counter | Router | 关键 Router 指标 | 按状态码和错误码累计 Router 返回的 HTTP 响应数。 |
|  | `smg_http_rate_limit_total` | HTTP 限流决策总数 | Counter | Router | 关键 Router 指标 | 按允许或拒绝结果累计 HTTP 限流决策次数。 |
|  | `smg_http_connections_active` | Router 活跃 HTTP 连接数 | Gauge | Router | 关键 Router 指标 | Router 当前活跃的 HTTP 连接数。 |
|  | `smg_router_requests_total` | 路由请求总数 | Counter | Router | 关键 Router 指标 | 按 Router 类型、后端类型、连接模式、模型、接口和流式模式累计路由请求数。 |
|  | `smg_router_request_errors_total` | 路由请求错误总数 | Counter | Router | 关键 Router 指标 | 按 Router、后端、连接模式、模型、接口和错误类型累计路由错误数。 |
|  | `smg_worker_pool_size` | Worker 池规模 | Gauge | Router | 关键 Router 指标 | 按 Worker 类型、连接模式和模型统计当前 Worker 数量。 |
|  | `smg_worker_requests_active` | Worker 活跃请求数 | Gauge | Router | 关键 Router 指标 | 每个 Worker 当前正在运行的请求数。 |
|  | `smg_worker_health` | Worker 健康状态 | Gauge | Router | 关键 Router 指标 | Worker 当前健康状态；健康为 1，不健康为 0。 |
|  | `smg_worker_retries_total` | Worker 重试总数 | Counter | Router | 关键 Router 指标 | 按 Worker 类型和接口累计重试次数。 |
|  | `smg_worker_retries_exhausted_total` | Worker 重试耗尽请求总数 | Counter | Router | 关键 Router 指标 | 按 Worker 类型和接口累计已耗尽全部重试机会的请求数。 |
|  | `smg_worker_cb_state` | Worker 熔断器状态 | Gauge | Router | 关键 Router 指标 | 每个 Worker 的熔断器状态：0 为关闭、1 为打开、2 为半开。 |
|  | `smg_http_request_duration_seconds` | Router HTTP 请求耗时 | Histogram | Router | Router 请求全链路时延 | 按 HTTP 方法和路径统计 Router 请求耗时分布，单位为秒。 |
|  | `smg_router_request_duration_seconds` | 路由请求耗时 | Histogram | Router | Router 请求全链路时延 | 按 Router 类型、后端类型、连接模式、模型和接口统计请求耗时分布。 |
|  | `smg_router_stage_duration_seconds` | Router 流水线阶段耗时 | Histogram | Router | Router 请求全链路时延 | gRPC Router 各流水线阶段的耗时分布。 |
|  | `smg_router_ttft_seconds` | Router 首 Token 延迟 | Histogram | Router | Router 请求全链路时延 | gRPC Router 观测的首 Token 延迟分布，单位为秒。 |
|  | `smg_router_tpot_seconds` | Router 单输出 Token 耗时 | Histogram | Router | Router 请求全链路时延 | gRPC Router 观测的每个输出 Token 平均耗时分布，单位为秒。 |
|  | `smg_router_generation_duration_seconds` | Router 生成总耗时 | Histogram | Router | Router 请求全链路时延 | gRPC Router 观测的完整生成过程耗时分布，单位为秒。 |
|  | `smg_http_inflight_request_age_count` | 处理中请求时长分布 | Gauge | Router | HTTP 与 Router 请求 | 按请求已处理时长划分的当前在途请求数；区间非累积，由 gt 和 le 标识。 |
|  | `smg_router_upstream_responses_total` | 上游响应总数 | Counter | Router | HTTP 与 Router 请求 | 按 Router 类型、HTTP 状态码和错误码累计上游后端响应数。 |
|  | `smg_router_tokens_total` | Router 处理 Token 总数 | Counter | Router | HTTP 与 Router 请求 | gRPC Router 按输入或输出类型累计处理的 Token 数。 |
|  | `smg_worker_connections_active` | Worker 活跃连接数 | Gauge | Router | Worker 池与健康状态 | 按 Worker 类型和连接模式统计当前活跃连接数。 |
|  | `smg_worker_health_checks_total` | Worker 健康检查总数 | Counter | Router | Worker 池与健康状态 | 按 Worker 类型和检查结果累计健康检查次数。 |
|  | `smg_worker_selection_total` | Worker 选择总数 | Counter | Router | Worker 池与健康状态 | 按 Worker 类型、连接模式、模型和策略累计 Worker 选择次数。 |
|  | `smg_worker_errors_total` | Worker 错误总数 | Counter | Router | Worker 池与健康状态 | 按 Worker 类型、连接模式和错误类型累计 Worker 级错误数。 |
|  | `smg_worker_routing_keys_active` | Worker 活跃路由键数 | Gauge | Router | Worker 池与健康状态 | 每个 Worker 当前关联的活跃路由键数量。 |
|  | `smg_manual_policy_cache_entries` | 手动路由策略缓存条目数 | Gauge | Router | 路由策略、熔断与重试 | 手动路由策略缓存中的当前路由条目数。 |
|  | `smg_manual_policy_branch_total` | 手动路由策略分支总数 | Counter | Router | 路由策略、熔断与重试 | 按分支累计手动路由策略的决策次数。 |
|  | `smg_consistent_hashing_policy_branch_total` | 一致性哈希策略分支总数 | Counter | Router | 路由策略、熔断与重试 | 按分支累计一致性哈希路由策略的决策次数。 |
|  | `smg_prefix_hash_policy_branch_total` | 前缀哈希策略分支总数 | Counter | Router | 路由策略、熔断与重试 | 按分支累计前缀哈希路由策略的决策次数。 |
|  | `smg_worker_cb_transitions_total` | 熔断器状态转换总数 | Counter | Router | 路由策略、熔断与重试 | 按 Worker、原状态和目标状态累计熔断器状态转换次数。 |
|  | `smg_worker_cb_outcomes_total` | 熔断器请求结果总数 | Counter | Router | 路由策略、熔断与重试 | 按 Worker 和成功或失败结果累计熔断器观测次数。 |
|  | `smg_worker_cb_consecutive_failures` | Worker 连续失败次数 | Gauge | Router | 路由策略、熔断与重试 | 每个 Worker 当前连续失败次数。 |
|  | `smg_worker_cb_consecutive_successes` | Worker 连续成功次数 | Gauge | Router | 路由策略、熔断与重试 | 每个 Worker 当前连续成功次数。 |
|  | `smg_worker_retry_backoff_seconds` | Worker 重试退避耗时 | Histogram | Router | 路由策略、熔断与重试 | 按重试次数统计退避等待时间分布，单位为秒。 |
|  | `smg_discovery_registrations_total` | Worker 注册尝试总数 | Counter | Router | 服务发现、MCP 与持久化 | 按发现来源和结果累计 Worker 注册尝试次数。 |
|  | `smg_discovery_deregistrations_total` | Worker 注销总数 | Counter | Router | 服务发现、MCP 与持久化 | 按发现来源和原因累计 Worker 注销事件数。 |
|  | `smg_discovery_sync_duration_seconds` | 服务发现同步耗时 | Histogram | Router | 服务发现、MCP 与持久化 | 按发现来源统计服务发现同步耗时分布，单位为秒。 |
|  | `smg_discovery_workers_discovered` | 服务发现 Worker 数 | Gauge | Router | 服务发现、MCP 与持久化 | 按发现来源统计当前已发现的 Worker 数量。 |
|  | `smg_mcp_tool_calls_total` | MCP 工具调用总数 | Counter | Router | 服务发现、MCP 与持久化 | 按模型、工具名和结果累计 MCP 工具调用次数。 |
|  | `smg_mcp_tool_duration_seconds` | MCP 工具执行耗时 | Histogram | Router | 服务发现、MCP 与持久化 | 按模型和工具名统计 MCP 工具执行耗时分布，单位为秒。 |
|  | `smg_mcp_servers_active` | 活跃 MCP Server 数 | Gauge | Router | 服务发现、MCP 与持久化 | 当前活跃的 MCP Server 连接数。 |
|  | `smg_mcp_tool_iterations_total` | MCP 工具循环迭代总数 | Counter | Router | 服务发现、MCP 与持久化 | 按模型累计 Responses API 工具循环的迭代次数。 |
|  | `smg_db_operations_total` | 数据库操作总数 | Counter | Router | 服务发现、MCP 与持久化 | 按存储类型、操作和结果累计数据库操作次数。 |
|  | `smg_db_operation_duration_seconds` | 数据库操作耗时 | Histogram | Router | 服务发现、MCP 与持久化 | 按存储类型和操作统计数据库操作耗时分布，单位为秒。 |
|  | `smg_db_connections_active` | 数据库活跃连接数 | Gauge | Router | 服务发现、MCP 与持久化 | 按存储类型统计当前活跃的数据库连接数。 |
|  | `smg_db_items_stored` | 数据库存储条目总数 | Counter | Router | 服务发现、MCP 与持久化 | 按存储类型累计写入的条目数；该指标虽无 _total 后缀，类型仍为 Counter。 |
|  | `router_mesh_convergence_ms` | Mesh 状态收敛耗时 | Histogram | Router | Router Mesh 集群 | Router 状态在 Mesh 中完成收敛的耗时分布，单位为毫秒。 |
|  | `router_mesh_batches_total` | Mesh 状态更新批次总数 | Counter | Router | Router Mesh 集群 | 按发送或接收方向及对端累计状态更新批次数。 |
|  | `router_mesh_bytes_total` | Mesh 传输字节总数 | Counter | Router | Router Mesh 集群 | 按发送或接收方向及对端累计 Mesh 传输字节数。 |
|  | `router_mesh_snapshot_trigger_total` | Mesh 快照触发总数 | Counter | Router | Router Mesh 集群 | 按存储和触发原因累计快照触发次数。 |
|  | `router_mesh_snapshot_duration_seconds` | Mesh 快照处理耗时 | Histogram | Router | Router Mesh 集群 | 按存储统计生成并发送快照的耗时分布，单位为秒。 |
|  | `router_mesh_snapshot_bytes_total` | Mesh 快照字节总数 | Counter | Router | Router Mesh 集群 | 按存储和传输方向累计快照字节数。 |
|  | `router_mesh_peer_connections` | Mesh 对端连接状态 | Gauge | Router | Router Mesh 集群 | 每个 Mesh 对端的连接状态；已连接为 1，未连接为 0。 |
|  | `router_mesh_peer_reconnects_total` | Mesh 对端重连总数 | Counter | Router | Router Mesh 集群 | 按对端累计 Mesh 重连次数。 |
|  | `router_mesh_peer_ack_total` | Mesh ACK 总数 | Counter | Router | Router Mesh 集群 | 按对端和成功或失败状态累计 ACK 消息数。 |
|  | `router_mesh_peer_nack_total` | Mesh NACK 总数 | Counter | Router | Router Mesh 集群 | 按对端累计 NACK 消息数。 |
|  | `router_mesh_store_cardinality` | Mesh 存储条目数 | Gauge | Router | Router Mesh 集群 | 每类 Mesh 状态存储中的当前条目数。 |
|  | `router_mesh_store_hash` | Mesh 存储状态哈希 | Gauge | Router | Router Mesh 集群 | 用于状态一致性检查的存储内容哈希值。 |
|  | `router_rl_drift_ratio` | 限流漂移比 | Gauge | Router | Router Mesh 集群 | 实际限流状态相对于预期状态的漂移比，按限流键区分。 |
|  | `router_lb_drift_ratio` | 负载均衡漂移比 | Gauge | Router | Router Mesh 集群 | 实际负载分配相对于预期分配的漂移比，按模型区分。 |
