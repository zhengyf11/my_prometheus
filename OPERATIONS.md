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
| `/etc/prometheus/rules/default.yml` | 默认告警规则 |
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
| `/var/lib/grafana` | Grafana 数据库、插件和运行数据 |

Dashboard 源文件与运行时文件不是同一份：

| Dashboard | 仓库源文件 | Grafana 实际读取文件 |
|---|---|---|
| Linux | `/opt/my_prometheus-installer/grafana/dashboards/node-overview.json` | `/var/lib/grafana/dashboards/linux/node-overview.json` |
| PD 合部 | `/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-unified.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json` |
| PD 分离与 Router | `/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-disaggregated.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json` |

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
| SGLang Dashboard 自动刷新 | 30 秒 | Dashboard JSON 根字段 `refresh` | 浏览器重新执行面板查询 |
| SGLang 默认时间范围 | 最近 6 小时 | Dashboard JSON 根字段 `time` | 初次打开看板的查询范围 |

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
    node: gpu-003
    endpoint: unified_30000

- targets: [10.30.0.3:30001]
  labels:
    role: sglang-prefill
    node: gpu-003
    endpoint: prefill_30001

- targets: [10.30.0.3:30002]
  labels:
    role: sglang-decode
    node: gpu-003
    endpoint: decode_30002

- targets: [10.30.0.3:30003]
  labels:
    role: sglang-router
    node: gpu-003
    endpoint: router_30003
```

不使用的角色应删除，不应保留默认占位地址。默认 `InstanceDown` 规则是 `up == 0`，占位 target 持续 `DOWN` 会形成无效告警。

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
| `panels[].targets[].expr` | 真正决定展示哪些指标的 PromQL |
| `panels[].targets[].legendFormat` | 图例名称 |
| `panels[].description` | 中文名称、Prometheus 原指标、类型、完整解释和特殊统计口径 |
| `panels[].fieldConfig` | 单位、阈值和颜色等展示配置 |
| `panels[].gridPos` | Dashboard 布局位置和尺寸 |

修改标题不会改变数据，修改 `targets[].expr` 才会改变查询内容。

### 6.3 Dashboard 变量

PD 合部看板变量：

```promql
label_values(up{job="file_sd_nodes",role="sglang-unified"}, instance)
label_values(sglang:num_requests_total{instance=~"$instance",engine_type="unified"}, model_name)
```

PD 分离与 Router 看板变量：

```promql
label_values(up{job="file_sd_nodes",role=~"sglang-prefill|sglang-decode|sglang-router"}, role)
label_values(up{job="file_sd_nodes",role=~"$role"}, instance)
label_values(sglang:num_requests_total{instance=~"$instance",role=~"$role",engine_type=~"prefill|decode"}, model_name)
```

变量内部名称保持为 `$role`、`$instance`、`$model`。界面标签显示为 `角色 (Role)`、`实例 (Instance)`、`模型 (Model)`。这些变量都支持多选和 All。

Role 下拉项不是在 Grafana 中写死的，而是来自 Prometheus 中 `up` 序列的 `role` 标签。因此 role 拼写不正确时，Dashboard 不会出现对应实例。

PD 分离与 Router 看板的每条 Panel PromQL 都直接包含 `role=~"$role"`，PD 合部看板的每条查询则固定包含 `role="sglang-unified"`。这避免不同角色使用相同 `instance` 或指标名时发生串数据。Grafana 的静态 Dashboard JSON 不能根据变量动态隐藏任意面板，因此选择 Router 后，PD 专属面板仍会保留布局，但只会显示 `No data`，不会继续展示 PD 样本。

### 6.4 面板查询

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

模型级 Engine 指标严格使用 `model_name=~"$model"`，并按 `role, instance, model_name` 聚合。HTTP、进程等实例级指标没有 `model_name` 标签，查询不添加模型过滤，只按 `role, instance` 聚合；这些面板不受模型 (Model) 下拉框影响。Router 当前至少保留 `role, instance`，更细的 `model`、`worker`、`endpoint` 和错误类型维度由对应专项面板处理。

普通 Histogram 面板只使用两类查询：

- P95：`histogram_quantile(0.95, ...)`
- 平均值：`rate(<metric>_sum) / rate(<metric>_count)`

所有 P80 查询已删除。每个普通指标独占一个面板，避免把语义或单位不同的指标画在同一纵轴上。生成器根据指标语义设置 Grafana 单位，例如延迟使用 `s` 或 `ms`、KV 传输量使用 `MB`、带宽使用 `GB/s`、比例使用 `0-100%`、Token 吞吐使用 `Token/s`。启动容量、页大小、上下文长度和其他启动后通常不变化的指标使用 Stat 数字面板，并通过 instant query 读取当前值。

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

### 6.5 面板名称、映射和分类

指标面板标题采用 `中文名称（大致解释）`，不再在标题或图例中显示原始指标名。完整映射保留在两个位置：

- `grafana/sglang-translations.json`：中文名称、原指标名和说明的结构化来源。
- `panels[].description`：Grafana 面板信息中显示中文名称、Prometheus 原指标、类型和完整说明。

对于 Counter，结构化翻译仍描述原始累计指标，面板标题则根据 `rate()` 查询派生为速率语义；Panel description 会明确写出“每秒速率，不是累计总数”。

生成器将高频观察项放在 `关键引擎指标`、`关键 Router 指标` 分组，将请求路径中的各阶段耗时集中放在 `请求全链路时延`、`Router 请求全链路时延` 分组。指标只从原分类移动到这些优先分组，不会重复生成。

### 6.6 翻译和重新生成

SGLang Dashboard 由生成器维护，不建议直接大规模手改生成后的 JSON：

```text
grafana/sglang-translations.json
tools/generate_sglang_dashboards.py
              |
              v
grafana/dashboards/sglang-pd-unified.json
grafana/dashboards/sglang-pd-disaggregated.json
```

修改后执行：

```bash
cd /opt/my_prometheus-installer
python3 tools/generate_sglang_dashboards.py
python3 tools/generate_sglang_translation_catalog.py
python3 -m unittest discover -s tests -v
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/sglang-pd-unified.json \
  /var/lib/grafana/dashboards/sglang/sglang-pd-unified.json
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/sglang-pd-disaggregated.json \
  /var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json
```

翻译评审文档 `docs/SGLang_Dashboard_中文翻译候选.md` 从结构化 JSON 生成。只有需要导入人工编辑过的 Markdown 时才执行：

```bash
python3 tools/import_sglang_translation_catalog.py
```

Grafana 运行时文件被修改后，provider 最多约 30 秒重新扫描。通过 Grafana UI 保存的修改可能在下次部署时被仓库源文件覆盖，正式修改应回到仓库并提交 Git。

## 7. 配置保护和重复部署

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

## 8. 状态、日志和验证

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

## 9. 常见问题定位

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
