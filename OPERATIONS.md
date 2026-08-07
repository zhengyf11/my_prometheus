# my_prometheus 安装与运维手册

## 1. 下载、安装、使用、停止与卸载

### 1.1 下载代码

Ubuntu/Debian 使用 `ubuntu` 分支：

```bash
git clone -b ubuntu https://github.com/Lamron-Karl/my_prometheus.git
cd my_prometheus
```

CentOS/RHEL 也可以使用该分支，安装器会自动选择 `apt-get`、`dnf` 或 `yum`。

运行环境要求：root 权限、Python 3.6+、systemd，以及能够访问 GitHub release 和 Grafana 官方软件源的网络。

### 1.2 安装

先演练安装过程，不修改系统：

```bash
sudo python3 install.py --yes --dry-run
```

执行默认安装：

```bash
sudo python3 install.py --yes
```

默认安装 Prometheus、Node Exporter 和 Grafana，不安装 Alertmanager。需要 Alertmanager 时执行：

```bash
sudo python3 install.py --yes --install-alertmanager
```

首次安装会生成 Grafana `admin` 密码。密码会在安装结束时显示，并保存到仅 root 可读的文件：

```bash
sudo cat /var/lib/my_prometheus/grafana-admin-credentials.json
```

### 1.3 安装完成后的服务与端口

| 服务 | systemd unit | 默认监听 | 用途 |
|---|---|---|---|
| Prometheus | `prometheus` | `0.0.0.0:9090` | 抓取、存储和查询监控指标 |
| Grafana | `grafana-server` | `0.0.0.0:3000` | Web 可视化面板 |
| Node Exporter | `node_exporter` | `127.0.0.1:9100` | 采集本机 CPU、内存、磁盘和网络指标 |
| Alertmanager | `alertmanager` | `0.0.0.0:9093` | 可选的告警接收与分发服务 |

安装器会设置已安装服务开机自启。Node Exporter 默认只允许本机 Prometheus 访问，不对外暴露。

### 1.4 在网页中查看监控

服务器网络可直达时，打开：

```text
Prometheus: http://<服务器IP>:9090
Grafana:    http://<服务器IP>:3000
```

Grafana 使用 `admin` 和上面凭据文件中的密码登录。安装器会创建两个 Dashboard 目录：

- `Linux Hosts`：包含 `Linux Node Overview`，使用真实的本机 Prometheus 数据源。
- `SGLang`：包含 `SGLang PD Unified Metrics` 和 `SGLang PD Disaggregated and Router Metrics` 两套看板。后者的 `Role` 下拉框支持单选、多选和 All，可组合查看 Prefill、Decode 与 Router。

Linux 与 SGLang 看板统一使用 Grafana 数据源 `Prometheus`，地址为 `http://localhost:9090`。SGLang 两套看板通过 Prometheus target 的 `role` 标签区分 PD 合部、Prefill、Decode 和 Router。安装器默认写入四个不可达的占位 target，因此看板结构和 Instance 下拉项可见，但 target 会显示 `DOWN`，业务指标暂时显示 No data。

Dashboard JSON 分为仓库源文件和安装后的运行时文件：

| Dashboard | 仓库源文件 | Grafana 实际加载文件 |
|---|---|---|
| Linux Node Overview | `grafana/dashboards/node-overview.json` | `/var/lib/grafana/dashboards/linux/node-overview.json` |
| SGLang PD Unified Metrics | `grafana/dashboards/sglang-pd-unified.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json` |
| SGLang PD Disaggregated and Router Metrics | `grafana/dashboards/sglang-pd-disaggregated.json` | `/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json` |

Grafana 的 dashboard provider 配置位于：

```text
/etc/grafana/provisioning/dashboards/dashboards.yml
```

provider 每 30 秒分别扫描 `/var/lib/grafana/dashboards/linux` 和 `/var/lib/grafana/dashboards/sglang`。修改仓库源文件后，需要重新执行安装器，或者将 JSON 复制到对应运行时目录；只修改仓库文件不会自动影响正在运行的 Grafana。

服务器只开放 SSH 时，可以建立本地隧道：

```bash
ssh -L 3000:127.0.0.1:3000 \
    -L 9090:127.0.0.1:9090 \
    root@<服务器地址>
```

然后在本机访问 `http://127.0.0.1:3000` 和 `http://127.0.0.1:9090`。

### 1.5 查看、停止和重新启动

查看简要状态：

```bash
systemctl is-active prometheus node_exporter grafana-server alertmanager
systemctl is-enabled prometheus node_exporter grafana-server alertmanager
```

查看详细状态和日志：

```bash
systemctl status prometheus node_exporter grafana-server --no-pager
journalctl -u prometheus -u node_exporter -u grafana-server -n 200 --no-pager
```

只停止本次默认安装的服务，仍保留开机自启：

```bash
sudo systemctl stop prometheus node_exporter grafana-server
```

停止并取消开机自启：

```bash
sudo systemctl disable --now prometheus node_exporter grafana-server
```

重新启动并恢复开机自启：

```bash
sudo systemctl enable --now prometheus node_exporter grafana-server
```

启用了 Alertmanager 时，在上述命令末尾增加 `alertmanager`。

### 1.6 卸载

先查看卸载动作，不修改系统：

```bash
sudo python3 uninstall.py --yes --dry-run
```

执行保守卸载：

```bash
sudo python3 uninstall.py --yes
```

保守卸载会停止并取消服务自启，删除本项目安装的二进制、managed 配置、Grafana provisioning、软件源和安装状态。只有安装状态明确记录 Grafana 是由本项目首次安装时，才会自动删除 Grafana 软件包；旧安装状态无法判断归属时默认保留 Grafana。

确认旧环境中的 Grafana 也应删除时执行：

```bash
sudo python3 uninstall.py --yes --remove-grafana
```

默认保留以下数据目录：

```text
/var/lib/prometheus
/var/lib/grafana
/var/lib/alertmanager
```

彻底删除数据和专用系统用户：

```bash
sudo python3 uninstall.py --yes --purge-data
```

同时删除安装器可能添加的 `3000`、`9090`、`9093` 防火墙规则：

```bash
sudo python3 uninstall.py --yes --purge-data --remove-firewall-rules
```

防火墙规则默认保留，因为旧版本状态文件没有记录规则是否在安装前已经存在。用户修改过且不带 managed 标记的配置默认不会删除；确认需要强制删除时增加 `--force`。

## 2. 03-gpu 部署位置与状态检查

03-gpu 对应节点：

```text
主机名：ydhh-gpu-003
内网 IP：10.20.0.3
公网 SSH：117.187.188.18:33003
```

登录命令：

```bash
ssh -p 33003 root@117.187.188.18
```

源码部署目录：

```text
/opt/my_prometheus-installer
```

主要运行时目录：

```text
/opt/my_prometheus                         下载和解压目录
/usr/local/bin/prometheus                  Prometheus 二进制
/usr/local/bin/node_exporter               Node Exporter 二进制
/etc/prometheus                            Prometheus 配置
/var/lib/prometheus                        Prometheus 数据
/etc/grafana                               Grafana 配置
/etc/grafana/provisioning/dashboards/dashboards.yml  Dashboard provider
/var/lib/grafana/dashboards/linux/node-overview.json                Node dashboard 运行时文件
/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json           PD 合部 dashboard 运行时文件
/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json     PD 分离与 Router dashboard 运行时文件
/opt/my_prometheus-installer/grafana/dashboards/node-overview.json    Node dashboard 源文件
/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-unified.json        PD 合部 dashboard 源文件
/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-disaggregated.json  PD 分离与 Router dashboard 源文件
/var/lib/my_prometheus                     安装状态和 Grafana 凭据
/etc/systemd/system/prometheus.service     Prometheus unit
/etc/systemd/system/node_exporter.service  Node Exporter unit
```

### 2.1 03 节点配置流

03 节点上，从“指定采集源”到“Grafana 加载 Dashboard”的配置关系如下：

```text
/etc/prometheus/targets/*.yml
  指定采集目标 IP:端口和附加标签
              |
              v
/etc/prometheus/prometheus.yml
  file_sd_configs 引用 targets 目录，定义抓取周期和 job
              |
              v
/etc/systemd/system/prometheus.service
  --config.file 指定 Prometheus 主配置

/etc/grafana/provisioning/datasources/prometheus.yml
  指定 Grafana 查询的 Prometheus 地址和数据源 UID
              |
              v
/etc/grafana/provisioning/dashboards/dashboards.yml
  指定 Grafana 扫描 Dashboard JSON 的目录
              |
              v
/var/lib/grafana/dashboards/linux/*.json
/var/lib/grafana/dashboards/sglang/*.json
  定义页面、变量、面板和 PromQL
```

各文件在 03 节点上的当前作用：

| 配置职责 | 03 节点文件 | 当前关键配置 |
|---|---|---|
| Prometheus 进程入口 | `/etc/systemd/system/prometheus.service` | `--config.file=/etc/prometheus/prometheus.yml`、数据目录 `/var/lib/prometheus`、监听 `0.0.0.0:9090` |
| Prometheus 主配置 | `/etc/prometheus/prometheus.yml` | 每 15 秒抓取一次；`file_sd_nodes` job 每 30 秒读取 `/etc/prometheus/targets/*.yml` |
| 本机 Node Exporter 目标 | `/etc/prometheus/targets/nodes.yml` | `127.0.0.1:9100`，附加 `role: local` |
| SGLang 看板占位目标 | `/etc/prometheus/targets/sglang-dashboards.yml` | 四个默认不可达地址，分别附加合部、Prefill、Decode、Router 角色 |
| SGLang 目标 | `/etc/prometheus/targets/03-sglang.yml` | 指定 SGLang 服务的 IP、端口以及 `role`、`node`、`endpoint` 标签 |
| Grafana 数据源 | `/etc/grafana/provisioning/datasources/prometheus.yml` | Linux 与 SGLang 统一使用 `Prometheus`，指向本机 `http://localhost:9090` |
| Dashboard provider | `/etc/grafana/provisioning/dashboards/dashboards.yml` | 分别把 `linux` 运行时目录加载到 `Linux Hosts`，把 `sglang` 运行时目录加载到 `SGLang` |
| Node Dashboard | `/var/lib/grafana/dashboards/linux/node-overview.json` | 定义 Linux Node Overview 的面板和 PromQL |
| SGLang Dashboards | `/var/lib/grafana/dashboards/sglang/*.json` | 定义 PD 合部，以及 PD 分离与 Router 两套面板及 PromQL |

#### 2.1.1 指标采集与页面刷新周期

Prometheus 请求各 target `/metrics` 的默认周期由 03 节点运行时配置指定：

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

仓库中的来源关系是：

```text
my_prometheus/prometheus.py
  scrape_interval = 15s
              |
              v
templates/prometheus.yml.tpl
  global.scrape_interval: ${scrape_interval}
              |
              v
/etc/prometheus/prometheus.yml
  global.scrape_interval: 15s
```

各时间配置的作用不同：

| 配置 | 当前值 | 作用 |
|---|---:|---|
| `/etc/prometheus/prometheus.yml` 的 `global.scrape_interval` | 15 秒 | Prometheus 向每个 target 请求 `/metrics` 的默认采集周期 |
| 同文件某个 `scrape_configs[]` job 内的 `scrape_interval` | 当前未单独设置 | 可覆盖全局值，只调整该 job 的采集周期 |
| `file_sd_configs[].refresh_interval` | 30 秒 | 重新扫描 `/etc/prometheus/targets/*.yml` 的周期，不是指标采集周期 |
| `global.evaluation_interval` | 15 秒 | 执行 recording/alerting rules 的周期，不是抓取周期 |
| Dashboard JSON 顶层 `refresh` | 30 秒 | 浏览器打开看板时重新执行 PromQL 的周期，不改变 Prometheus 采集频率 |
| Grafana provider 的 `updateIntervalSeconds` | 30 秒 | 扫描 Dashboard JSON 文件变更的周期，不改变指标采集频率 |

临时修改 03 节点采集周期时，编辑 `/etc/prometheus/prometheus.yml`，校验后热加载：

```bash
vi /etc/prometheus/prometheus.yml
promtool check config /etc/prometheus/prometheus.yml
curl -fsS -X POST http://127.0.0.1:9090/-/reload
```

如果希望重新执行安装器后仍保持新默认值，还要同步修改 `my_prometheus/prometheus.py` 中传给模板的 `scrape_interval`；否则后续带 `--force` 的安装可能重新生成 15 秒配置。

仓库文件与 03 节点运行时文件的对应关系：

| 仓库源文件 | 安装器处理逻辑 | 03 节点运行时文件 |
|---|---|---|
| `templates/prometheus.yml.tpl` | `my_prometheus/prometheus.py` 渲染模板 | `/etc/prometheus/prometheus.yml` |
| `templates/nodes.yml.tpl` | `my_prometheus/prometheus.py` 首次创建并保留后续人工修改 | `/etc/prometheus/targets/nodes.yml` |
| `templates/sglang-targets.yml.tpl` | `my_prometheus/prometheus.py` 首次创建四类占位 target，并保留后续人工修改 | `/etc/prometheus/targets/sglang-dashboards.yml` |
| 无仓库模板，由运维人员维护 | Prometheus 的 file SD 自动发现 | `/etc/prometheus/targets/03-sglang.yml` |
| `my_prometheus/grafana.py` 中的 `provision_datasource` | 安装器生成数据源配置 | `/etc/grafana/provisioning/datasources/prometheus.yml` |
| `my_prometheus/grafana.py` 中的 `provision_dashboards` | 安装器生成 provider 配置 | `/etc/grafana/provisioning/dashboards/dashboards.yml` |
| `grafana/dashboards/node-overview.json` | 安装器复制 JSON | `/var/lib/grafana/dashboards/linux/node-overview.json` |
| `grafana/dashboards/sglang-pd-unified.json` | 安装器复制 JSON | `/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json` |
| `grafana/dashboards/sglang-pd-disaggregated.json` | 安装器复制 JSON | `/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json` |

03 节点上的仓库副本位于 `/opt/my_prometheus-installer`。例如 PD 合部 Dashboard 存在两份文件：

```text
/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-unified.json  仓库源文件
/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json              Grafana 实际读取的运行时文件
```

Grafana 不直接读取 `/opt/my_prometheus-installer`。只更新仓库源文件不会改变当前页面，必须重新执行安装器，或者把源 JSON 发布到 `/var/lib/grafana/dashboards`。

### 2.2 03 节点数据流

03 节点上一次完整的指标读取过程如下：

```text
SGLang /metrics 或 Node Exporter /metrics
              |
              | HTTP GET，默认路径 /metrics
              v
Prometheus :9090
  按 targets 文件中的地址抓取
  添加 job、instance 以及 targets 文件中声明的标签
  保存到 /var/lib/prometheus
              |
              | PromQL 查询
              v
Grafana datasource
  Linux 与 SGLang: UID Prometheus -> http://localhost:9090
              |
              v
Dashboard JSON 中的变量和 panel targets
              |
              v
浏览器访问 http://10.20.0.3:3000
```

具体到当前 SGLang Dashboard：

1. `/etc/prometheus/targets/03-sglang.yml` 指定采集源，目前配置了 `10.30.0.3:30000` 和 `10.30.0.2:31001`。
2. `/etc/prometheus/prometheus.yml` 中的 `file_sd_nodes` job 发现该文件。target 中没有配置 `metrics_path` 时，Prometheus 默认请求 `http://<IP>:<端口>/metrics`。
3. Prometheus 将目标地址写入 `instance` 标签，将 job 写为 `file_sd_nodes`，并保留 target 文件声明的 `role`、`node`、`endpoint` 标签。
4. Linux 和两套 SGLang Dashboard 都通过 UID `Prometheus` 查询本机 `http://localhost:9090`。
5. SGLang 看板通过 `role` 筛选 Instance，再使用 `$instance` 等变量查询 `sglang:*`、`smg_*` 或 `router_*` 指标；区别在 target 标签，不在数据源。
6. `/etc/prometheus/targets/sglang-dashboards.yml` 中的占位 target 即使抓取失败也会生成值为 0 的 `up` 序列，因此 Instance 下拉项存在，但业务指标没有数据。

当前 `/etc/prometheus/targets/03-sglang.yml` 的生效内容是：

```yaml
- targets:
    - 10.30.0.3:30000
  labels:
    role: sglang
    node: ydhh-gpu-003
    endpoint: gpu_03_30000

- targets:
    - 10.30.0.2:31001
  labels:
    role: sglang
    node: ydhh-gpu-003
    endpoint: gpu_04_31001
```

这里的 `node` 和 `endpoint` 是人工附加的展示标签，不决定网络访问地址；真正的采集地址由 `targets` 中的 `IP:端口` 决定。

安装器还会根据仓库中的 `templates/sglang-targets.yml.tpl` 首次创建 `/etc/prometheus/targets/sglang-dashboards.yml`：

```yaml
- targets: [127.0.0.1:39000]
  labels: {role: sglang-unified, node: placeholder, endpoint: placeholder_unified}
- targets: [127.0.0.1:39001]
  labels: {role: sglang-prefill, node: placeholder, endpoint: placeholder_prefill}
- targets: [127.0.0.1:39002]
  labels: {role: sglang-decode, node: placeholder, endpoint: placeholder_decode}
- targets: [127.0.0.1:39003]
  labels: {role: sglang-router, node: placeholder, endpoint: placeholder_router}
```

这些地址只用于预置四类 target，不要求端口上有进程。接入真实服务时编辑此文件，把对应 `targets`、`node` 和 `endpoint` 替换成实际值并保留正确的 `role`；不使用的角色可以删除整个条目。file SD 会在约 30 秒内自动发现修改，无需新建 Grafana 数据源，也无需重启 Prometheus。

### 2.3 Dashboard 中展示哪些数据

Dashboard 展示哪些数据，不是在 `dashboards.yml` provider 中配置的。`dashboards.yml` 只告诉 Grafana 去哪个目录加载 JSON；具体面板、数据查询和下拉变量都定义在 Dashboard JSON 内。

当前两个 SGLang Dashboard 的仓库源文件是：

```text
/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-unified.json
/opt/my_prometheus-installer/grafana/dashboards/sglang-pd-disaggregated.json
```

Grafana 实际读取的是：

```text
/var/lib/grafana/dashboards/sglang/sglang-pd-unified.json
/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json
```

Dashboard JSON 中与数据有关的主要结构是：

```text
panels[]
  datasource                 该面板使用哪个 Grafana 数据源
  targets[]
    expr                     查询哪些指标以及如何聚合
    legendFormat             查询结果在图例中的名称
    refId                    同一面板内查询的标识 A、B、C...
  title                      面板标题
  type                       timeseries、stat 等展示类型
  fieldConfig                单位、颜色、阈值等展示设置

templating.list[]
  name                       变量名，例如 instance、model
  datasource                 变量从哪个数据源查询
  query.query                下拉选项查询
  multi/includeAll/allValue  是否支持多选和 All
```

#### 2.3.1 面板使用哪个数据源

每个面板的 `datasource` 指向 Grafana 数据源 UID：

```json
"datasource": {
  "type": "prometheus",
  "uid": "Prometheus"
}
```

这里的 `uid: Prometheus` 对应 `/etc/grafana/provisioning/datasources/prometheus.yml` 中的：

```yaml
datasources:
  - name: Prometheus
    uid: Prometheus
    type: prometheus
    url: http://localhost:9090
```

Dashboard 不直接连接 SGLang，而是把 PromQL 发给本机 Prometheus。Prometheus 再按 `/etc/prometheus/targets/*.yml` 抓取不同的 SGLang 地址；因此新增或替换实例时修改 target 地址和 `role`，不需要创建新的 Grafana 数据源。

#### 2.3.2 面板查询哪些指标

真正决定某个面板展示哪些数据的是：

```text
panels[].targets[].expr
```

例如 `Token Throughput` 面板配置了两条查询：

```json
"targets": [
  {
    "expr": "sum by (instance) (rate(sglang:prompt_tokens_total{instance=~\"$instance\",model_name=~\"$model\"}[$__rate_interval]))",
    "legendFormat": "{{instance}} prompt",
    "refId": "A"
  },
  {
    "expr": "sum by (instance) (rate(sglang:generation_tokens_total{instance=~\"$instance\",model_name=~\"$model\"}[$__rate_interval]))",
    "legendFormat": "{{instance}} generation",
    "refId": "B"
  }
],
"title": "Token Throughput",
"type": "timeseries"
```

这个面板的数据含义是：

| 配置 | 作用 |
|---|---|
| `sglang:prompt_tokens_total` | 输入/prefill Token 累计数 |
| `sglang:generation_tokens_total` | 输出 Token 累计数 |
| `rate(...[$__rate_interval])` | 转换成 Grafana 当前时间范围内的每秒速率 |
| `instance=~"$instance"` | 只查询 Instance 下拉框选中的实例 |
| `model_name=~"$model"` | 只查询 Model 下拉框选中的模型 |
| `sum by (instance)` | 按实例汇总，同时保留实例维度 |
| `legendFormat` | 设置图例名称，不改变查询结果 |

再例如 `Time to First Token` 面板使用 `sglang:time_to_first_token_seconds_bucket`，通过三条 `expr` 分别计算 P80、P95 和平均值。P95 查询为：

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(sglang:time_to_first_token_seconds_bucket{
      instance=~"$instance",
      model_name=~"$model"
    }[$__rate_interval])
  )
)
```

要增加、删除或替换一个面板的数据，需要修改对应 panel 的 `targets` 数组。`title`、`type`、`fieldConfig` 只负责标题和展示方式，不决定从 Prometheus 读取哪些指标。

#### 2.3.3 Instance 下拉列表

Dashboard 顶部的 `Instance` 下拉列表配置在：

```text
templating.list[] 中 name 为 instance 的对象
```

PD 合部 Dashboard 的关键配置是：

```json
{
  "name": "instance",
  "label": "Instance",
  "type": "query",
  "datasource": {
    "type": "prometheus",
    "uid": "Prometheus"
  },
  "definition": "label_values(up{job=\"file_sd_nodes\",role=\"sglang-unified\"}, instance)",
  "query": {
    "query": "label_values(up{job=\"file_sd_nodes\",role=\"sglang-unified\"}, instance)"
  },
  "multi": true,
  "includeAll": true,
  "allValue": ".*"
}
```

决定下拉选项的是：

```promql
label_values(up{job="file_sd_nodes",role="sglang-unified"}, instance)
```

其生成过程如下：

```text
/etc/prometheus/targets/03-sglang.yml
  targets: 10.30.0.3:30000
  labels.role: sglang-unified
              |
              v
Prometheus 生成时间序列
up{
  job="file_sd_nodes",
  role="sglang-unified",
  instance="10.30.0.3:30000"
}
              |
              v
Dashboard 变量查询 instance 标签
              |
              v
Instance 下拉列表出现 10.30.0.3:30000
```

因此，Instance 下拉列表中的内容不是直接写死在 Dashboard JSON 中的，而是同时由以下两处决定：

1. `/etc/prometheus/targets/*.yml` 中有哪些 target，以及 target 带什么 `role` 标签。
2. Dashboard 变量查询中的 job 和 role 过滤条件。

`up` 指标在 target 抓取失败时仍然存在，只是值为 0，所以 DOWN 的目标也可以保留在 Instance 下拉列表中。

两套 Dashboard 使用以下角色条件：

| Dashboard | Instance 变量查询 |
|---|---|
| PD 合部 | `label_values(up{job="file_sd_nodes",role="sglang-unified"}, instance)` |
| PD 分离与 Router | Role 支持多选和 All：先选择 `role=sglang-prefill|sglang-decode|sglang-router`，再用 `label_values(up{job="file_sd_nodes",role=~"$role"}, instance)` |

当前 03 节点旧 target 使用的是 `role: sglang`，与两套新 Dashboard 的角色条件不同。所有看板使用同一个 Prometheus，但实际 SGLang target 必须按上表标记角色，才能进入对应看板的 Instance 下拉列表。

#### 2.3.4 Model 下拉列表

PD 合部和 PD 分离 Dashboard 都有 `Model` 下拉列表，配置在 `templating.list[]` 中 `name` 为 `model` 的对象。PD 合部查询是：

```promql
label_values(
  sglang:num_requests_total{instance=~"$instance",engine_type="unified"},
  model_name
)
```

PD 分离查询使用 `engine_type=~"prefill|decode"`。它们都从所选实例的 `sglang:num_requests_total` 指标中提取 `model_name` 标签。合并看板选择 Router 时，Model 下拉框可能为空；Router 查询不会使用 `$model` 过滤条件。

Engine 面板查询使用 `model_name=~"$model|^$"`：所选模型会过滤带 `model_name` 的指标，`|^$` 同时保留没有该标签的 HTTP、进程等全局指标。

手工修改变量 JSON 时，应同步修改 `definition` 和 `query.query`，避免导入或后续 UI 编辑时显示不一致。

#### 2.3.5 两套 Dashboard 的指标范围

两个 Dashboard 已按部署模式拆分：

| Dashboard | 指标范围 | 完整指标族数量 |
|---|---|---:|
| SGLang PD Unified Metrics | `sglang:*`，`engine_type="unified"` 对应的合部 Engine | 122 |
| SGLang PD Disaggregated and Router Metrics | `sglang:*` Engine 全集，以及 Router `smg_*`、Router Mesh `router_*`；通过 Role 切换 | 183 |

指标按模块分类成 Row；每个指标族至少出现在一个 `panels[].targets[].expr` 中。Counter 面板展示 `rate`，Histogram 面板展示 P80、P95 和通过 `_sum / _count` 计算的平均值，Gauge/Summary 面板展示当前序列。功能未启用或事件尚未发生时，懒创建指标显示 No data 属于正常现象。

Router 面板查询示例：

```promql
sum by (instance) (
  rate(smg_http_requests_total{instance=~"$instance"}[$__rate_interval])
)
```

Router target 必须使用 `role: sglang-router`。在合并看板中选择该 Role 后，Router 分类面板显示数据，Engine 分类面板显示 No data；选择 Prefill 或 Decode 时行为相反。

### 2.4 Router 指标与现有 Dashboard 的关系

03 节点当前 Router 的业务 API 监听 `8000`，Prometheus 指标独立监听 `29000`：

```text
http://127.0.0.1:8000/metrics   返回 404，8000 是业务 API 端口
http://127.0.0.1:29000/metrics  返回 200，29000 是 Router metrics 端口
```

当前 `/etc/prometheus/targets/03-sglang.yml` 尚未配置 `10.30.0.3:29000`，因此合并看板选择 Router 时不会显示该进程的实时指标。接入时应给 Router target 使用独立的 `role`：

```yaml
- targets:
    - 10.30.0.3:29000
  labels:
    role: sglang-router
    node: ydhh-gpu-003
    endpoint: gpu_03_router_29000
```

该示例只说明配置关系，不代表 03 节点已经写入此配置。

### 2.5 配置修改后的生效方式

| 修改内容 | 生效方式 |
|---|---|
| `/etc/prometheus/targets/*.yml` | file SD 最多约 30 秒自动发现，不需要重启 Prometheus |
| `/etc/prometheus/prometheus.yml` | 先用 `promtool check config` 校验，再调用 `POST /-/reload` 或重启 Prometheus |
| `/etc/grafana/provisioning/datasources/prometheus.yml` | 重启 `grafana-server` 重新执行 provisioning |
| `/etc/grafana/provisioning/dashboards/dashboards.yml` | 重启 `grafana-server` 重新加载 provider |
| `/var/lib/grafana/dashboards/linux/*.json`、`/var/lib/grafana/dashboards/sglang/*.json` | provider 最多约 30 秒自动扫描，不需要重启 Grafana |
| `/opt/my_prometheus-installer/grafana/dashboards/*.json` | 只是仓库源文件；发布到运行时目录后才影响页面 |

Prometheus 主配置修改后的校验和热加载命令：

```bash
promtool check config /etc/prometheus/prometheus.yml
curl -fsS -X POST http://127.0.0.1:9090/-/reload
```

查看 file SD 实际发现了哪些目标：

```bash
curl -fsS http://127.0.0.1:9090/api/v1/targets | jq \
  '.data.activeTargets[] | {scrapeUrl, health, labels, lastError}'
```

确认 Grafana 当前加载的数据源和 Dashboard 文件：

```bash
sed -n '1,160p' /etc/grafana/provisioning/datasources/prometheus.yml
sed -n '1,160p' /etc/grafana/provisioning/dashboards/dashboards.yml
ls -l /var/lib/grafana/dashboards
```

### 2.6 状态检查

查看 03-gpu 当前服务状态：

```bash
systemctl is-active prometheus node_exporter grafana-server
systemctl is-enabled prometheus node_exporter grafana-server
systemctl status prometheus node_exporter grafana-server --no-pager
```

查看相关进程和监听端口：

```bash
pgrep -a -f 'prometheus|node_exporter|grafana'
ss -lntp | grep -E ':(3000|9090|9093|9100)[[:space:]]'
```

查看最近日志：

```bash
journalctl -u prometheus -u node_exporter -u grafana-server -n 200 --no-pager
```

检查 HTTP 健康状态：

```bash
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:9100/metrics >/dev/null
curl -fsS http://127.0.0.1:3000/api/health
```

本次更新完成后，03-gpu 的三个服务应保持 `inactive` 且不会由更新代码自动拉起。需要恢复时再手动执行：

```bash
systemctl enable --now prometheus node_exporter grafana-server
```
