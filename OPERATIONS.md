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

Grafana 使用 `admin` 和上面凭据文件中的密码登录。安装器已经创建 Prometheus 数据源，并在 `Linux Hosts` 目录中导入：

- `Linux Node Overview`：主机 CPU、内存、磁盘和网络状态。
- `SGLang Inference Overview`：SGLang 流量、token 吞吐、请求队列、延迟、KV Cache、运行时利用率、推测解码和引擎容量。

SGLang dashboard 顶部可以按 `Instance` 和 `Model` 筛选，同一套面板可切换查看 `10.30.0.3:30000`、`10.30.0.2:31001` 等采集目标。

Dashboard JSON 分为仓库源文件和安装后的运行时文件：

| Dashboard | 仓库源文件 | Grafana 实际加载文件 |
|---|---|---|
| Linux Node Overview | `grafana/dashboards/node-overview.json` | `/var/lib/grafana/dashboards/node-overview.json` |
| SGLang Inference Overview | `grafana/dashboards/sglang-overview.json` | `/var/lib/grafana/dashboards/sglang-overview.json` |

Grafana 的 dashboard provider 配置位于：

```text
/etc/grafana/provisioning/dashboards/dashboards.yml
```

该 provider 每 30 秒扫描一次 `/var/lib/grafana/dashboards`。修改仓库源文件后，需要重新执行安装器，或者将 JSON 复制到运行时目录；只修改仓库文件不会自动影响正在运行的 Grafana。

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
/var/lib/grafana/dashboards/node-overview.json       Node dashboard 运行时文件
/var/lib/grafana/dashboards/sglang-overview.json     SGLang dashboard 运行时文件
/opt/my_prometheus-installer/grafana/dashboards/node-overview.json    Node dashboard 源文件
/opt/my_prometheus-installer/grafana/dashboards/sglang-overview.json  SGLang dashboard 源文件
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
/var/lib/grafana/dashboards/*.json
  定义页面、变量、面板和 PromQL
```

各文件在 03 节点上的当前作用：

| 配置职责 | 03 节点文件 | 当前关键配置 |
|---|---|---|
| Prometheus 进程入口 | `/etc/systemd/system/prometheus.service` | `--config.file=/etc/prometheus/prometheus.yml`、数据目录 `/var/lib/prometheus`、监听 `0.0.0.0:9090` |
| Prometheus 主配置 | `/etc/prometheus/prometheus.yml` | 每 15 秒抓取一次；`file_sd_nodes` job 每 30 秒读取 `/etc/prometheus/targets/*.yml` |
| 本机 Node Exporter 目标 | `/etc/prometheus/targets/nodes.yml` | `127.0.0.1:9100`，附加 `role: local` |
| SGLang 目标 | `/etc/prometheus/targets/03-sglang.yml` | 指定 SGLang 服务的 IP、端口以及 `role`、`node`、`endpoint` 标签 |
| Grafana 数据源 | `/etc/grafana/provisioning/datasources/prometheus.yml` | 数据源名称和 UID 均为 `Prometheus`，查询 `http://localhost:9090` |
| Dashboard provider | `/etc/grafana/provisioning/dashboards/dashboards.yml` | 每 30 秒扫描 `/var/lib/grafana/dashboards`，在 `Linux Hosts` 文件夹中加载 JSON |
| Node Dashboard | `/var/lib/grafana/dashboards/node-overview.json` | 定义 Linux Node Overview 的面板和 PromQL |
| SGLang Dashboard | `/var/lib/grafana/dashboards/sglang-overview.json` | 定义 SGLang Inference Overview 的变量、面板和 PromQL |

仓库文件与 03 节点运行时文件的对应关系：

| 仓库源文件 | 安装器处理逻辑 | 03 节点运行时文件 |
|---|---|---|
| `templates/prometheus.yml.tpl` | `my_prometheus/prometheus.py` 渲染模板 | `/etc/prometheus/prometheus.yml` |
| `templates/nodes.yml.tpl` | `my_prometheus/prometheus.py` 首次创建并保留后续人工修改 | `/etc/prometheus/targets/nodes.yml` |
| 无仓库模板，由运维人员维护 | Prometheus 的 file SD 自动发现 | `/etc/prometheus/targets/03-sglang.yml` |
| `my_prometheus/grafana.py` 中的 `provision_datasource` | 安装器生成数据源配置 | `/etc/grafana/provisioning/datasources/prometheus.yml` |
| `my_prometheus/grafana.py` 中的 `provision_dashboards` | 安装器生成 provider 配置 | `/etc/grafana/provisioning/dashboards/dashboards.yml` |
| `grafana/dashboards/node-overview.json` | 安装器复制 JSON | `/var/lib/grafana/dashboards/node-overview.json` |
| `grafana/dashboards/sglang-overview.json` | 安装器复制 JSON | `/var/lib/grafana/dashboards/sglang-overview.json` |

03 节点上的仓库副本位于 `/opt/my_prometheus-installer`。例如 SGLang Dashboard 存在两份文件：

```text
/opt/my_prometheus-installer/grafana/dashboards/sglang-overview.json  仓库源文件
/var/lib/grafana/dashboards/sglang-overview.json                    Grafana 实际读取的运行时文件
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
Grafana Prometheus datasource（UID: Prometheus）
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
3. Prometheus 将目标地址写入 `instance` 标签，将 job 写为 `file_sd_nodes`，并保留 target 文件声明的 `role="sglang"`、`node`、`endpoint` 标签。
4. Grafana 数据源配置把 Dashboard 的 PromQL 发送到本机 `http://localhost:9090`。
5. `sglang-overview.json` 使用数据源 UID `Prometheus`。`Instance` 变量来自 `up{job="file_sd_nodes",role="sglang"}`，`Model` 变量来自 `sglang:num_requests_total` 的 `model_name` 标签。
6. 各面板再使用 `$instance`、`$model` 查询 `sglang:*` 指标并完成分类展示。

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

### 2.3 Router 指标与现有 Dashboard 的关系

03 节点当前 Router 的业务 API 监听 `8000`，Prometheus 指标独立监听 `29000`：

```text
http://127.0.0.1:8000/metrics   返回 404，8000 是业务 API 端口
http://127.0.0.1:29000/metrics  返回 200，29000 是 Router metrics 端口
```

当前 `/etc/prometheus/targets/03-sglang.yml` 尚未配置 `10.30.0.3:29000`，因此 Prometheus 和 Grafana 不会自动看到 Router 指标。即使后续加入该 target，现有 `SGLang Inference Overview` 主要查询 `sglang:*` 指标，而 Router 暴露的是 `smg_*` 指标，不能直接复用现有面板；应给 Router 使用独立的 `role` 和独立 Dashboard，例如：

```yaml
- targets:
    - 10.30.0.3:29000
  labels:
    role: sglang-router
    node: ydhh-gpu-003
    endpoint: gpu_03_router_29000
```

该示例只说明配置关系，不代表 03 节点已经写入此配置。

### 2.4 配置修改后的生效方式

| 修改内容 | 生效方式 |
|---|---|
| `/etc/prometheus/targets/*.yml` | file SD 最多约 30 秒自动发现，不需要重启 Prometheus |
| `/etc/prometheus/prometheus.yml` | 先用 `promtool check config` 校验，再调用 `POST /-/reload` 或重启 Prometheus |
| `/etc/grafana/provisioning/datasources/prometheus.yml` | 重启 `grafana-server` 重新执行 provisioning |
| `/etc/grafana/provisioning/dashboards/dashboards.yml` | 重启 `grafana-server` 重新加载 provider |
| `/var/lib/grafana/dashboards/*.json` | provider 最多约 30 秒自动扫描，不需要重启 Grafana |
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

### 2.5 状态检查

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
