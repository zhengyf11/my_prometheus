# my_prometheus 部署后运维说明

本文说明部署完成后的目录、配置流、数据流、采集周期、Dashboard 配置和常用维护操作。首次安装、SGLang 接入、网页访问和卸载流程见 [README.md](README.md)。

## 1. 默认目录与文件

### 1.1 源码与安装产物

文档约定的源码目录是：

```text
/opt/my_prometheus-installer
```

该目录由 `git clone` 的目标路径决定，安装器不会自动复制或移动源码。运维命令应从这个目录执行：

```bash
cd /opt/my_prometheus-installer
```

主要路径如下：

| 类型 | 默认路径 | 作用 |
|---|---|---|
| 源码仓库 | `/opt/my_prometheus-installer` | 安装器、模板、Dashboard 源文件和文档 |
| 下载与解压目录 | `/opt/my_prometheus` | Prometheus 组件压缩包及解压结果 |
| 下载缓存 | `/opt/my_prometheus/downloads` | Release tarball、RPM 等下载缓存 |
| 可执行文件 | `/usr/local/bin` | `prometheus`、`promtool`、`node_exporter` 等 |
| 安装状态 | `/var/lib/my_prometheus/install-state.json` | 版本、Grafana 归属等卸载依据 |
| Grafana 凭据 | `/var/lib/my_prometheus/grafana-admin-credentials.json` | 自动生成的管理员账号密码，权限 `0600` |

### 1.2 Prometheus 文件

| 文件或目录 | 作用 |
|---|---|
| `/etc/prometheus/prometheus.yml` | Prometheus 主配置、抓取 job、规则目录和全局周期 |
| `/etc/prometheus/targets/nodes.yml` | 额外 Linux Node Exporter target |
| `/etc/prometheus/targets/sglang-dashboards.yml` | SGLang unified、prefill、decode、router target |
| `/etc/prometheus/targets/*.yml` | `file_sd_nodes` job 自动发现的全部 target 文件 |
| `/etc/prometheus/rules/default.yml` | 默认 recording rules 和告警规则 |
| `/var/lib/prometheus` | Prometheus TSDB 数据 |
| `/etc/systemd/system/prometheus.service` | Prometheus systemd unit |
| `/etc/systemd/system/node_exporter.service` | Node Exporter systemd unit |

本机 Node Exporter 已在 `/etc/prometheus/prometheus.yml` 的 `node_exporter` 静态 job 中采集。因此 `nodes.yml` 只应放额外远端节点；仅监控本机时建议内容为 `[]`，避免同一个 target 被重复采集。

### 1.3 Grafana 文件

| 文件或目录 | 作用 |
|---|---|
| `/etc/grafana/grafana.ini` | Grafana 监听地址、端口和用户设置 |
| `/etc/grafana/provisioning/datasources/prometheus.yml` | Prometheus 数据源定义 |
| `/etc/grafana/provisioning/dashboards/dashboards.yml` | Dashboard provider 和扫描目录 |
| `/var/lib/grafana/dashboards/linux/node-overview.json` | Linux Dashboard 运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json` | PD 合部 Dashboard 运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json` | PD 分离与 Router Dashboard 运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-service-overview.json` | SGLang 服务总览运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-pd-pipeline.json` | PD 链路运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-engine-scheduler.json` | Engine/Scheduler 运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-router-worker.json` | Router/Worker 运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-kv-capacity.json` | KV/容量运行时文件 |
| `/var/lib/grafana/dashboards/sglang/sglang-optional-features.json` | 可选功能运行时文件 |
| `/var/lib/grafana` | Grafana 数据库、插件和运行数据 |

Dashboard 源文件与运行时文件不是同一份：

| Dashboard | 仓库源文件 | Grafana 实际读取文件 |
|---|---|---|
| Linux | `/opt/my_prometheus-installer/grafana/dashboards/node-overview.json` | `/var/lib/grafana/dashboards/linux/node-overview.json` |
| PD 合部 | `/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-unified.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json` |
| PD 分离与 Router | `/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-disaggregated.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json` |
| 六张运维看板 | `/opt/my_prometheus-installer/grafana/dashboards/sglang-{service-overview,pd-pipeline,engine-scheduler,router-worker,kv-capacity,optional-features}.json` | `/var/lib/grafana/dashboards/sglang/` 下的同名文件 |

只修改仓库源文件不会改变当前 Grafana 页面。必须重新执行安装器，或把生成后的 JSON 发布到对应运行时目录。

### 1.4 Alertmanager 文件

仅在安装 Alertmanager 时存在：

| 文件或目录 | 作用 |
|---|---|
| `/etc/alertmanager/alertmanager.yml` | 路由和 receiver 配置 |
| `/var/lib/alertmanager` | Alertmanager 数据 |
| `/etc/systemd/system/alertmanager.service` | systemd unit |

默认 receiver 为空，不会自动把告警发送到邮件、即时通信或 webhook。

## 2. 配置流

### 2.1 指标采集配置流

```text
/etc/systemd/system/prometheus.service
  --config.file=/etc/prometheus/prometheus.yml
                         |
                         v
/etc/prometheus/prometheus.yml
  定义 scrape_configs、rule_files、采集周期
                         |
                         v
/etc/prometheus/targets/*.yml
  定义 file_sd target 的 IP:端口和 role/node/endpoint 标签
                         |
                         v
Prometheus 自动发现并抓取 target
```

对应仓库生成关系：

```text
my_prometheus/prometheus.py
          +
templates/prometheus.yml.tpl
          +
templates/nodes.yml.tpl
          +
templates/sglang-targets.yml.tpl
          |
          v
/etc/prometheus/prometheus.yml
/etc/prometheus/targets/nodes.yml
/etc/prometheus/targets/sglang-dashboards.yml
```

`nodes.yml` 和 `sglang-dashboards.yml` 首次创建后默认保留人工修改。重新执行安装器不会覆盖它们，除非显式使用 `--force`。

### 2.2 Grafana 配置流

```text
/etc/grafana/provisioning/datasources/prometheus.yml
  定义 UID=Prometheus -> http://localhost:9090
                         |
                         v
/etc/grafana/provisioning/dashboards/dashboards.yml
  Linux Hosts -> /var/lib/grafana/dashboards/linux
  SGLang      -> /var/lib/grafana/dashboards/sglang
                         |
                         v
/var/lib/grafana/dashboards/**/*.json
  定义变量、Row、Panel、PromQL、图例、单位和布局
                         |
                         v
Grafana Web 页面
```

`dashboards.yml` 只负责“从哪里加载 Dashboard”，不决定 Dashboard 展示哪些指标。具体指标由 Dashboard JSON 的 `panels[].targets[].expr` 决定。

## 3. 数据流

```text
Node Exporter /metrics 或 SGLang /metrics
                         |
                         | HTTP GET，默认每 15 秒
                         v
Prometheus :9090
  添加 job、instance 和 file_sd 自定义标签
  规则计算并写入 /var/lib/prometheus
                         |
                         | Grafana 通过 PromQL 查询
                         v
Grafana 数据源 UID Prometheus
  URL: http://localhost:9090
                         |
                         v
Dashboard 变量和 Panel
                         |
                         v
浏览器 :3000
```

关键标签来源：

| 标签 | 来源 | 作用 |
|---|---|---|
| `job` | `/etc/prometheus/prometheus.yml` 中的 job 名 | SGLang file_sd target 当前为 `file_sd_nodes` |
| `instance` | Prometheus 根据 target 地址自动生成 | 通常等于 `<IP>:<端口>` |
| `role` | `/etc/prometheus/targets/*.yml` | 区分 unified、prefill、decode、router |
| `expected` | `/etc/prometheus/targets/*.yml` | `true` 表示正式纳管，`false` 表示预留且不进入 SGLang 健康状态/InstanceDown 告警 |
| `node` | target 文件人工配置 | 标识机器或部署节点 |
| `endpoint` | target 文件人工配置 | 标识端口或业务端点 |
| `model_name` | SGLang 指标自身标签 | Dashboard 的模型筛选依据 |

Prometheus target 仅配置 `IP:端口` 时，默认访问：

```text
http://<IP>:<端口>/metrics
```

如果实际接口不是 HTTP `/metrics`，需要新增独立 scrape job，并配置 `scheme`、`metrics_path`、认证或 TLS 参数。

## 4. 默认时间配置

| 时间配置 | 默认值 | 配置位置 | 作用 |
|---|---:|---|---|
| 指标抓取周期 | 15 秒 | `/etc/prometheus/prometheus.yml` 的 `global.scrape_interval` | Prometheus 请求 target `/metrics` |
| 规则计算周期 | 15 秒 | `/etc/prometheus/prometheus.yml` 的 `global.evaluation_interval` | 计算告警和 recording rule |
| file_sd 刷新周期 | 30 秒 | `scrape_configs[].file_sd_configs[].refresh_interval` | 重新读取 `/etc/prometheus/targets/*.yml` |
| Dashboard provider 扫描周期 | 30 秒 | `/etc/grafana/provisioning/dashboards/dashboards.yml` | 重新扫描运行时 Dashboard JSON |
| SGLang Dashboard 自动刷新 | 总览/PD 链路 30 秒，详情 1 分钟 | Dashboard JSON 根字段 `refresh` | 历史绝对时间复盘时手动设为 Off |
| SGLang 默认时间范围 | 最近 6 小时 | Dashboard JSON 根字段 `time` | 初次打开看板的查询范围 |

Grafana 不能根据“绝对历史时间”或“相对实时范围”自动切换刷新。分享事故复盘链接时，应在刷新下拉框选择 `Off`，或删除 URL 中的 `refresh` 参数；实时值班时保留默认刷新。

仓库中的采集周期来源是：

```text
my_prometheus/prometheus.py
  scrape_interval = 15s
  evaluation_interval = 15s
            |
            v
templates/prometheus.yml.tpl
            |
            v
/etc/prometheus/prometheus.yml
```

只修改运行时 `/etc/prometheus/prometheus.yml` 会立即影响当前节点，但以后重新生成 managed 配置可能恢复仓库默认值。要修改项目默认值，应同时修改仓库生成逻辑、测试和文档。

修改主配置后执行：

```bash
sudo /usr/local/bin/promtool check config /etc/prometheus/prometheus.yml
curl -fsS -X POST http://127.0.0.1:9090/-/reload
```

修改 file_sd target 通常无需 reload，等待最多约 30 秒即可。

## 5. SGLang target 配置

运行时文件：

```text
/etc/prometheus/targets/sglang-dashboards.yml
```

角色必须使用：

```text
sglang-unified
sglang-prefill
sglang-decode
sglang-router
```

示例：

```yaml
# Managed by my_prometheus install.py
- targets: [10.30.0.3:30000]
  labels:
    role: sglang-unified
    expected: "true"
    node: gpu-003
    endpoint: unified_30000

- targets: [10.30.0.3:30001]
  labels:
    role: sglang-prefill
    expected: "true"
    node: gpu-003
    endpoint: prefill_30001

- targets: [10.30.0.3:30002]
  labels:
    role: sglang-decode
    expected: "true"
    node: gpu-003
    endpoint: decode_30002

- targets: [10.30.0.3:30003]
  labels:
    role: sglang-router
    expected: "true"
    node: gpu-003
    endpoint: router_30003
```

正式投入监控的目标设置 `expected: "true"`。预留但尚未启用的地址设置 `expected: "false"`，SGLang 看板和 `InstanceDown` 告警会排除它；完全不需要的占位地址仍建议删除。

编辑安装器创建的 target 文件时必须保留第一行 `# Managed by my_prometheus install.py`。如果希望由其他配置管理系统维护 target，可以新建另一个 `/etc/prometheus/targets/*.yml` 文件；该文件不会被本项目卸载器删除。

检查 target：

```bash
curl -fsS http://127.0.0.1:9090/api/v1/targets \
  | python3 -m json.tool
```

查询各角色状态：

```bash
curl -fsSG http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=up{job="file_sd_nodes",role=~"sglang-.*"}' \
  | python3 -m json.tool
```

## 6. Dashboard 展示配置

### 6.1 数据源和加载目录

所有 Dashboard 共用一个 Prometheus 数据源：

```yaml
# /etc/grafana/provisioning/datasources/prometheus.yml
datasources:
  - name: Prometheus
    uid: Prometheus
    type: prometheus
    url: http://localhost:9090
```

Dashboard JSON 中通过固定 UID 引用：

```json
"datasource": {
  "type": "prometheus",
  "uid": "Prometheus"
}
```

不同 SGLang 服务不需要创建多个 Grafana 数据源。它们由 Prometheus target 的 `instance` 和 `role` 标签区分。

### 6.2 Dashboard JSON 的关键字段

| JSON 字段 | 作用 |
|---|---|
| `uid` | Dashboard 稳定标识，URL 使用该值 |
| `title` | Dashboard 标题 |
| `refresh` | 页面自动刷新周期 |
| `time` | 默认查询时间范围 |
| `templating.list[]` | Role、Instance、Model 等下拉变量 |
| `panels[]` | Row、说明面板和指标面板 |
| `panels[].collapsed` | Row 是否默认折叠；折叠 Row 的子面板存放在该 Row 的 `panels[]` 中 |
| `panels[].targets[].expr` | 真正决定展示哪些指标的 PromQL |
| `panels[].targets[].legendFormat` | 图例名称 |
| `panels[].description` | 中文名称、Prometheus 原指标、类型、完整解释和特殊统计口径 |
| `panels[].fieldConfig` | 单位、阈值和颜色等展示配置 |
| `panels[].gridPos` | Dashboard 布局位置和尺寸 |

修改标题不会改变数据，修改 `targets[].expr` 才会改变查询内容。

### 6.3 Dashboard 变量

PD 合部看板变量：

```promql
label_values(up{job="file_sd_nodes",expected="true",role="sglang-unified"}, instance)
label_values(sglang:num_requests_total{instance=~"$instance",engine_type="unified"}, model_name)
```

PD 分离与 Router 看板变量：

```promql
label_values(up{job="file_sd_nodes",expected="true",role=~"sglang-prefill|sglang-decode|sglang-router"}, role)
label_values(up{job="file_sd_nodes",expected="true",role=~"$role"}, instance)
label_values(sglang:num_requests_total{instance=~"$instance",role=~"$role",engine_type=~"prefill|decode"}, model_name)
```

变量内部名称保持为 `$role`、`$instance`、`$model`。界面标签显示为 `角色 (Role)`、`实例 (Instance)`、`模型 (Model)`。这些变量都支持多选和 All。

当前 target 和 SGLang exporter 没有统一提供 `cluster`、`namespace`、`service`、`version` 标签，因此不创建永远为空的下拉变量。需要这些维度时，应先在 `/etc/prometheus/targets/*.yml` 的 `labels` 中统一补齐，再扩展 Dashboard 变量与每条 PromQL。当前依赖顺序为 Role -> Instance -> Model，避免 Role All 直接展开无关实例。

Role 下拉项不是在 Grafana 中写死的，而是来自 Prometheus 中 `up` 序列的 `role` 标签。因此 role 拼写不正确时，Dashboard 不会出现对应实例。

PD 分离与 Router 看板的普通 PromQL 包含 `role=~"$role"`，PD 合部查询固定为 `role="sglang-unified"`。Prefill Token 指标额外固定 `role="sglang-prefill"`，Decode Token 指标额外固定 `role="sglang-decode"`；Role 未选择对应阶段时查询为空。跨角色的 Prefill/Decode 吞吐比按模型全局计算，不受 Role/Instance 变量影响，面板说明中会明确标注。Grafana 静态 JSON 无法根据查询结果可靠地自动隐藏任意面板，因此不适用面板可能保留布局。

### 6.4 采集健康与 No data 判断

两个 SGLang 看板顶部都有“采集健康 (Scrape Health)”分组。该分组查询的是 Prometheus 自动生成的采集指标，不依赖 SGLang 是否注册某个业务指标：

| 面板 | Prometheus 指标或口径 | 用途 |
|---|---|---|
| 采集目标状态 | `up{expected="true"}` | `1` 为抓取成功，`0` 为正式纳管目标抓取失败；Node Exporter 和预留目标不混入 |
| 纳管目标数 | `count(up{expected="true",...})` | Prometheus 服务发现中正式纳管的目标数；无法推断未写入 target 文件的外部期望数量 |
| 最近成功采集距今时间 | 最近 24 小时 `up == 1` 的最后样本 | 绿色 <30 秒、黄色 >=30 秒、红色 >=60 秒 |
| 每次采集样本数 | `scrape_samples_scraped` | 识别 exporter 无样本或指标数量异常下降 |
| 采集耗时 | `scrape_duration_seconds` | 识别 exporter 变慢或接近抓取超时 |
| SGLang 记录规则数量 | `prometheus_rule_group_rules` | 确认 `sglang.recording` 规则组已加载，当前应为 41 |
| 规则评估失败增量 | `increase(prometheus_rule_evaluation_failures_total[5m])` | 0 为正常，大于 0 时检查 Rules 页面和日志 |

因此，业务面板出现 `No data` 时应先检查采集健康。只有 target 为 `UP`、采集新鲜、样本数非 0 且规则无失败后，才继续判断角色不适用、功能未启用、尚未触发或版本变化。已确认懒注册的错误 Counter 使用请求 Counter 作为零值基线：错误指标不存在但请求指标存在时显示 0；二者都不存在时保留 No data。所有时序面板的 `spanNulls` 为 `false`。

### 6.5 面板查询

每个面板的查询位于：

```text
panels[].targets[].expr
```

例如速率类指标：

```promql
sum by (role, instance, model_name) (
  rate(sglang:prompt_tokens_total{
    instance=~"$instance",
    role="sglang-unified",
    model_name=~"$model"
  }[$__rate_interval])
)
```

Counter 原指标表示进程启动以来的累计值，但趋势面板统一使用 `rate()`，因此标题和单位必须表达每秒速率。例如：

| 原始指标 | 面板标题 | 查询口径 |
|---|---|---|
| `sglang:num_requests_total` | 请求完成速率 | request/s |
| `sglang:prompt_tokens_total` | Prefill 吞吐 | Token/s |
| `sglang:generation_tokens_total` | Decode 吞吐 | Token/s |

在 PD 分离部署中，`sglang:num_requests_total` 表示 Prefill/Decode 各阶段完成速率，同一请求可能在两个阶段分别计数，不能相加当作客户 RPS。客户入口速率使用 Router 的 `smg_router_requests_total`。Prefill 吞吐固定查询 `sglang-prefill`，Decode 吞吐固定查询 `sglang-decode`。

模型级 Engine 指标严格使用 `model_name=~"$model"`，并按 `role, instance, model_name` 聚合。HTTP、进程等实例级指标没有 `model_name` 标签，查询不添加模型过滤，只按 `role, instance` 聚合；这些面板不受模型 (Model) 下拉框影响。Router 当前至少保留 `role, instance`，更细的 `model`、`worker`、`endpoint` 和错误类型维度由对应专项面板处理。

普通 Histogram 面板使用两类查询：

- P95：`histogram_quantile(0.95, ...)`
- 平均值：`rate(<metric>_sum) / rate(<metric>_count)`

TTFT、ITL、端到端延迟、KV 传输延迟以及 Router 核心时延同时展示 P50、P95、P99，不展示平均值或 P80。这些查询使用 `recording_rule or 原始 histogram_quantile(...)`：当前窗口优先使用预计算结果，早于规则创建时间的历史窗口自动使用原始 bucket。每个普通指标独占一个面板并使用严格匹配的单位。启动后通常不变化的指标使用 Stat。趋势图图例使用 Current/Max，不显示容易掩盖峰值的 Mean；区间总量必须使用独立的 `increase(...[$__range])`，不能把速率采样值的 Sum 当作总量。

输入 Token 长度分段为：

```text
0-4k, 4k-15k, 15k-60k, 60k-300k, 300k-1M, 1M+
```

生成 Token 长度分段为：

```text
0-500, 500-2k, 2k-8k, 8k-30k, 30k-100k, 100k+
```

分段面板使用 `increase(<metric>_bucket[$__range])` 计算当前 Dashboard 时间范围内的请求数，并用相邻累计 bucket 相减得到各区间。查询使用 SGLang 默认导出的输入边界 `4000/15000/60000/300000/1000000` 和生成边界 `500/2000/8000/30000/100000`，不需要修改 SGLang 启动参数。最后一个区间使用 `<metric>_count - 最后一个有限 bucket` 计算；最外层使用 `round()` 消除 `increase()` 时间边界外推产生的小数，按整数展示请求个数。升级 SGLang 后如果默认 bucket 发生变化，需要同步修改生成器和测试。

未缓存输入 Token Histogram 不单独展示。缓存命中率使用以下口径并限制在 `[0, 1]`：

```promql
1 - rate(sglang:uncached_prompt_tokens_histogram_sum)
    / rate(sglang:prompt_tokens_histogram_sum)
```

`$__rate_interval` 由 Grafana 根据时间范围、面板宽度和数据源采集周期动态计算，不是固定的 15 秒。

### 6.6 面板名称、映射和分类

指标面板使用简短中文标题，缩写如 TTFT 可保留；英文名、解释和原始指标不再挤占标题。完整映射保留在两个位置：

- `grafana/sglang-translations.json`：中文名称、原指标名和说明的结构化来源。
- `panels[].description`：Grafana 面板信息中显示中文名称、Prometheus 原指标、类型和完整说明。

对于 Counter，结构化翻译仍描述原始累计指标，面板标题则根据 `rate()` 查询派生为速率语义；Panel description 会明确写出“每秒速率，不是累计总数”。

Service Overview 只展开 13 个核心业务面板，并以三个紧凑状态展示 target、新鲜度和规则失败；完整 183 指标目录保留在全量及专项看板。低频 Row 默认折叠，避免首次打开同时发起全部查询。

Router HTTP 响应面板只使用 `smg_http_responses_total`，先按 `status_code` 计算 2xx、5xx、429 的速率，再除以全部响应速率得到占比。健康 Worker 面板对 `smg_worker_health` 求和。当前该指标没有 `worker_type` 或模型标签，因此只能展示健康 Worker 总数，不能可靠拆成健康 Prefill/Decode Worker 数。

SGLang 指标中的 `sglang:utilization` 表示引擎调度利用率，不是 GPU 利用率；`sglang:startup_available_gpu_memory_gb` 只是启动时可用显存，不是运行时显存。真实 GPU 利用率和显存面板需要额外接入 DCGM Exporter 或 NVIDIA GPU Exporter，本项目当前没有这类数据源，因此不生成伪 GPU 面板。

两张全量指标看板用于兼容和指标查阅，刷新周期为 1 分钟，非核心 Row 默认折叠并把子面板嵌套在 Row 中，折叠时不会发起这些查询。六张运维看板按 `Service Overview`、`PD Pipeline`、`Engine / Scheduler`、`Router / Worker`、`KV / Capacity`、`Optional Features` 拆分；总览和 PD 链路使用 30 秒刷新，详情使用 1 分钟。核心 Histogram 面板优先查询 recording rules，并为历史窗口回退原始 bucket；高基数错误类面板使用 `topk(10)` 即时表格。

### 6.7 翻译和重新生成

SGLang Dashboard 由生成器维护，不建议直接大规模手改生成后的 JSON：

```text
grafana/sglang-translations.json
tools/generate_sglang_dashboards.py
              |
              v
grafana/dashboards/sglang-pd-unified.json
grafana/dashboards/sglang-pd-disaggregated.json
grafana/dashboards/sglang-service-overview.json
grafana/dashboards/sglang-pd-pipeline.json
grafana/dashboards/sglang-engine-scheduler.json
grafana/dashboards/sglang-router-worker.json
grafana/dashboards/sglang-kv-capacity.json
grafana/dashboards/sglang-optional-features.json
```

修改后执行：

```bash
cd /opt/my_prometheus-installer
python3 tools/generate_sglang_dashboards.py
python3 tools/generate_sglang_translation_catalog.py
python3 -m unittest discover -s tests -v
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/sglang-*.json \
  /var/lib/grafana/dashboards/sglang/
```

翻译评审文档 `docs/SGLang_Dashboard_中文翻译候选.md` 从结构化 JSON 生成。只有需要导入人工编辑过的 Markdown 时才执行：

```bash
python3 tools/import_sglang_translation_catalog.py
```

Grafana 运行时文件被修改后，provider 最多约 30 秒重新扫描。通过 Grafana UI 保存的修改可能在下次部署时被仓库源文件覆盖，正式修改应回到仓库并提交 Git。

## 7. Recording Rules 和告警

仓库模板为 `templates/rules.yml.tpl`，安装后写入 `/etc/prometheus/rules/default.yml`。Prometheus 每 15 秒计算规则，其中 SGLang recording group 显式使用 30 秒周期和 5 分钟速率窗口。

Recording rules 不会回填创建前的历史数据，因此 Dashboard 的核心分位和 12 个派生面板均保留等价原始查询作为 `or` 回退。回退提高历史复盘可用性，但扫描 Histogram bucket 的成本更高；实时窗口通常命中 recording rule。

主要派生指标如下：

| Recording rule | 含义 |
|---|---|
| `my_prometheus:sglang_request_rate:5m` | 按 Role/Instance/Model 的请求完成速率 |
| `my_prometheus:sglang_ttft_seconds_p50/p95/p99:5m` | TTFT 三个核心分位 |
| `my_prometheus:sglang_prefill_decode_throughput_ratio:5m` | Prefill/Decode 请求吞吐比 |
| `my_prometheus:sglang_prefill_decode_worker_capacity_ratio` | Router 注册的 Prefill/Decode Worker 容量比 |
| `my_prometheus:sglang_kv_transfer_failure_ratio:5m` | KV 传输失败请求比例 |
| `my_prometheus:sglang_bootstrap_failure_ratio:5m` | Bootstrap 失败请求比例 |
| `my_prometheus:sglang_prefill_retry_ratio:5m` | Prefill 重试比例 |
| `my_prometheus:sglang_kv_transfer_latency_ms_p99:5m` | KV 传输 P99 延迟 |
| `my_prometheus:sglang_kv_transfer_speed_gb_s_p99:5m` | KV 传输速度 P99 |
| `my_prometheus:sglang_router_error_ratio:5m` | Router 请求错误比例 |
| `my_prometheus:sglang_router_retry_exhausted_ratio:5m` | Router 重试耗尽比例 |
| `my_prometheus:sglang_router_healthy_workers` | Router 健康 Worker 总数 |
| `my_prometheus:sglang_router_open_circuit_breakers` | Open 状态的 Worker 熔断器数 |
| `my_prometheus:sglang_router_worker_load_skew` | Worker 活跃请求数的 Max/Avg |

默认确定性告警包括：

| Alert | 触发条件 |
|---|---|
| `InstanceDown` | `expected!="false"` 的 target 连续 2 分钟抓取失败；明确标记为预留的目标不告警 |
| `SGLangNoHealthyRouterWorkers` | Router 自身 UP，但健康 Worker 总数连续 2 分钟为 0 |
| `SGLangKVTransferFailure` | 最近 5 分钟出现 KV 传输失败 |
| `SGLangBootstrapFailure` | 最近 5 分钟出现 Bootstrap 失败 |
| `SGLangRouterRetryExhausted` | 最近 5 分钟出现重试耗尽 |
| `SGLangWorkerCircuitBreakerOpen` | Worker 熔断器连续 2 分钟为 Open |
| `SGLangRouterMeshDisconnected` | Router Mesh Peer 连接数连续 5 分钟为 0 |

以下告警没有默认阈值，因此不会在代码中猜测：错误率/429、TTFT/E2E P99、等待队列增长速度、KV Cache 使用率和可用槽位。启用前应根据模型、负载和容量测试确定阈值与持续时间。真实 GPU 显存/利用率告警还需要先接入 GPU exporter。

检查规则与当前状态：

```bash
sudo /usr/local/bin/promtool check rules /etc/prometheus/rules/default.yml
curl -fsS http://127.0.0.1:9090/api/v1/rules | python3 -m json.tool
curl -fsS http://127.0.0.1:9090/api/v1/alerts | python3 -m json.tool
```

Alertmanager 默认 receiver 为空；告警状态会在 Prometheus 中计算，但不会自动外发。通知路由配置见 `/etc/alertmanager/alertmanager.yml`。

## 8. 配置保护和重复部署

安装器生成的文本配置带有：

```text
Managed by my_prometheus install.py
```

处理规则：

- 文件不存在：创建。
- 文件内容未变化：保留。
- managed 文件变化：备份后更新。
- 非 managed 文件冲突：默认停止，避免覆盖。
- `nodes.yml` 和 `sglang-dashboards.yml`：不使用 `--force` 时保留人工修改。
- Dashboard 运行时文件与仓库不同：安装器默认停止，防止覆盖页面修改。

`--force` 不是常规升级参数。它会同时替换冲突 Dashboard、managed 配置以及两个 target 文件。使用前必须备份真实 target，并检查 `.bak.<时间戳>` 文件；只更新 Dashboard 时应使用上一节的定向 `install` 命令。

推荐更新过程：

```bash
cd /opt/my_prometheus-installer
git status --short --branch
old_commit="$(git rev-parse HEAD)"
git pull --ff-only
python3 -m unittest discover -s tests -v
git diff "$old_commit"..HEAD -- README.md OPERATIONS.md my_prometheus templates grafana
```

根据 diff 决定后续动作：Dashboard 使用定向发布；安装器代码或系统配置需要更新时，先执行 `sudo python3 install.py --yes --dry-run`，确认不会覆盖 target 后再执行正式安装。

## 9. 状态、日志和验证

服务状态：

```bash
systemctl status prometheus node_exporter grafana-server --no-pager
systemctl is-enabled prometheus node_exporter grafana-server
```

端口：

```bash
sudo ss -lntp | grep -E ':(3000|9090|9093|9100)\b'
```

日志：

```bash
journalctl -u prometheus -u node_exporter -u grafana-server \
  -n 200 --no-pager
```

配置和健康检查：

```bash
/usr/local/bin/promtool check config /etc/prometheus/prometheus.yml
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:9100/metrics >/dev/null
```

Grafana provisioning：

```bash
sudo sed -n '1,200p' /etc/grafana/provisioning/datasources/prometheus.yml
sudo sed -n '1,240p' /etc/grafana/provisioning/dashboards/dashboards.yml
```

## 10. 常见问题定位

### Target 为 DOWN

1. 从 Prometheus 节点执行 `curl http://<IP>:<端口>/metrics`。
2. 检查进程监听地址是否允许远程访问。
3. 检查路由、安全组和防火墙。
4. 检查 target 是否错误使用 `127.0.0.1`。
5. 检查 Prometheus target 页面的 `lastError`。

### Target 为 UP，但 Dashboard 没数据

1. 检查 `/metrics` 是否存在 Dashboard 使用的指标名。
2. 检查 `role` 是否为规定值。
3. 在 Prometheus 直接查询具体指标。
4. 选择正确的 Role、Instance 和 Model。
5. 触发真实业务请求；部分指标按需注册。

### 修改 Dashboard 后页面不变化

1. 确认修改的是运行时文件还是仓库源文件。
2. 重新执行安装器发布源文件。
3. 等待 provider 的 30 秒扫描周期。
4. 查看 `journalctl -u grafana-server` 是否有 provisioning 错误。

### 安装失败

1. 使用 `--verbose` 获取完整安装日志。
2. 检查 Python、systemd、端口和 root 权限。
3. 检查 GitHub Release、Grafana 仓库和系统软件源网络。
4. 受限网络使用 `--proxy`，并同步配置 apt/dnf/yum 代理。
5. 不要为了绕过未知冲突直接使用 `--force`。
