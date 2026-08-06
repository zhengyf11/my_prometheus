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

SGLang dashboard 顶部可以按 `Instance` 和 `Model` 筛选，同一套面板可切换查看 `127.0.0.1:30000`、`10.30.0.2:31001` 等采集目标。

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
