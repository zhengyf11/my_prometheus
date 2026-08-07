# my_prometheus

`my_prometheus` 是一个面向 systemd Linux 服务器的监控栈安装器，用于安装和配置：

- Prometheus `3.12.0`
- Node Exporter `1.11.1`
- Grafana OSS
- 可选的 Alertmanager `0.32.1`
- Linux 主机 Dashboard
- SGLang PD 合部、PD 分离及 Router Dashboard

本文用于完成新节点部署、SGLang 指标接入、网页查看和卸载。部署后的目录、配置流、数据流和 Dashboard 维护方式见 [OPERATIONS.md](OPERATIONS.md)。

## 1. 部署前准备

### 1.1 支持环境

- Ubuntu 20.04/22.04/24.04、Debian 11/12
- CentOS Stream 8/9、RHEL 8/9、Rocky Linux、AlmaLinux 等兼容系统
- systemd
- Python 3.6+
- `x86_64` 或 `aarch64`
- root 权限
- 可访问 GitHub Release 和 Grafana 官方软件源

精简系统先安装引导依赖。

Ubuntu/Debian：

```bash
sudo apt-get update
sudo apt-get install -y git python3 ca-certificates
```

RHEL/CentOS 系：

```bash
sudo dnf install -y git python3 ca-certificates
```

如果使用 `yum`，将上面的 `dnf` 替换为 `yum`。

### 1.2 部署前确认

默认端口如下：

| 服务 | 端口 | 默认监听地址 | 说明 |
|---|---:|---|---|
| Prometheus | 9090 | `0.0.0.0` | 无内置登录认证 |
| Grafana | 3000 | `0.0.0.0` | 使用 Grafana 用户登录 |
| Node Exporter | 9100 | `127.0.0.1` | 仅供本机 Prometheus 采集 |
| Alertmanager | 9093 | `0.0.0.0` | 默认不安装 |

执行安装前确认端口未被其他程序占用：

```bash
sudo ss -lntp | grep -E ':(3000|9090|9093|9100)\b' || true
```

默认配置会让 Prometheus 和 Grafana 对所有网卡监听，并在已启用的 UFW 或 firewalld 中开放端口。生产环境应先选择一种访问方式：

- 推荐：只监听 `127.0.0.1`，通过 SSH 隧道或反向代理访问。
- 内网直连：监听内网地址，并在安全组、防火墙中仅允许管理网段。
- 不建议：把未配置 TLS 和访问控制的 `9090`、`3000` 直接暴露到公网。

## 2. 下载与安装

### 2.1 下载代码

本文统一使用 `/opt/my_prometheus-installer` 作为源码目录：

```bash
sudo mkdir -p /opt/my_prometheus-installer
sudo chown "$(id -u):$(id -g)" /opt/my_prometheus-installer
git clone --branch ubuntu \
  https://github.com/Lamron-Karl/my_prometheus.git \
  /opt/my_prometheus-installer
cd /opt/my_prometheus-installer
```

部署前应确认当前 commit 是计划发布的版本：

```bash
git status --short --branch
git log -1 --oneline
```

源码必须先推送或合并到新节点可访问的远端分支。只存在于开发机本地的提交无法通过上述命令部署。

### 2.2 演练安装

演练会打印操作，但不修改系统：

```bash
sudo python3 install.py --yes --dry-run
```

### 2.3 推荐安装方式

推荐仅监听本机，再通过 SSH 隧道访问：

```bash
sudo python3 install.py \
  --yes \
  --prometheus-listen-address 127.0.0.1 \
  --grafana-listen-address 127.0.0.1 \
  --skip-firewall
```

需要在可信内网中直接访问时，可以执行默认安装：

```bash
sudo python3 install.py --yes
```

需要 Alertmanager 时增加：

```bash
sudo python3 install.py --yes --install-alertmanager
```

Alertmanager 的默认配置没有邮件或 webhook 接收方。安装完成只代表服务可用，发送实际通知还需要配置 `/etc/alertmanager/alertmanager.yml`。

常用可选参数：

```bash
sudo python3 install.py \
  --yes \
  --grafana-version '<固定版本>' \
  --retention-time 15d \
  --download-timeout 300 \
  --download-retries 3 \
  --proxy http://proxy.example:8080
```

正式环境建议固定 Grafana 版本，避免重复部署时自动安装不同的 `latest` 版本。

## 3. 安装结果检查

### 3.1 查看服务

```bash
systemctl is-active prometheus node_exporter grafana-server
systemctl is-enabled prometheus node_exporter grafana-server
```

启用了 Alertmanager 时再检查：

```bash
systemctl is-active alertmanager
```

### 3.2 查看 HTTP 健康状态

```bash
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:9100/metrics >/dev/null
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:9090/api/v1/targets
```

安装器会自动检查 Prometheus、Node Exporter、Grafana 和本机基础 target。SGLang 默认还是占位 target，因此在接入真实地址前显示 `DOWN` 是预期现象。

### 3.3 Grafana 密码

首次安装时，如果没有传入密码，安装器会生成 `admin` 密码并保存到仅 root 可读的文件：

```bash
sudo cat /var/lib/my_prometheus/grafana-admin-credentials.json
```

也可以在首次安装时通过环境变量指定，避免把密码直接写进 shell 历史：

```bash
export GRAFANA_ADMIN_PASSWORD='<强密码>'
sudo -E python3 install.py --yes
unset GRAFANA_ADMIN_PASSWORD
```

需要重置密码时：

```bash
export GRAFANA_ADMIN_PASSWORD='<新密码>'
sudo -E python3 install.py \
  --yes \
  --reset-grafana-admin-password
unset GRAFANA_ADMIN_PASSWORD
```

## 4. 配置 SGLang IP 和端口

### 4.1 先验证指标接口

必须从 Prometheus 所在节点验证网络连通性：

```bash
curl -fsS http://<SGLang-IP>:<端口>/metrics | head
```

target 文件只填写 `IP:端口`。当前 Prometheus job 默认使用 HTTP，并自动请求 `/metrics`。如果接口使用其他路径、HTTPS 或认证，需要在 `/etc/prometheus/prometheus.yml` 中增加独立的 `scrape_config`，不能只修改 target 文件。

### 4.2 替换占位 target

编辑安装后文件：

```bash
sudo vi /etc/prometheus/targets/sglang-dashboards.yml
```

编辑时保留文件第一行的 managed 标记，安装器依靠它识别文件归属：

```text
# Managed by my_prometheus install.py
```

PD 合部示例：

```yaml
# Managed by my_prometheus install.py
- targets:
    - 10.30.0.3:30000
  labels:
    role: sglang-unified
    node: gpu-003
    endpoint: unified_30000
```

PD 分离和 Router 示例：

```yaml
# Managed by my_prometheus install.py
- targets:
    - 10.30.0.3:30001
  labels:
    role: sglang-prefill
    node: gpu-003
    endpoint: prefill_30001

- targets:
    - 10.30.0.3:30002
  labels:
    role: sglang-decode
    node: gpu-003
    endpoint: decode_30002

- targets:
    - 10.30.0.3:30003
  labels:
    role: sglang-router
    node: gpu-003
    endpoint: router_30003
```

`role` 必须使用下列值，否则对应 Dashboard 的下拉框不会发现实例：

| 部署角色 | `role` 标签 |
|---|---|
| PD 合部 | `sglang-unified` |
| Prefill | `sglang-prefill` |
| Decode | `sglang-decode` |
| Router | `sglang-router` |

注意事项：

- 删除未使用的占位条目，不要让 `127.0.0.1:39000-39003` 长期保留为 `DOWN`。
- `targets` 决定实际网络地址；`node` 和 `endpoint` 是便于识别的附加标签。
- Prometheus 必须能访问该 IP 和端口。SGLang 与 Prometheus 在同一台机器时才使用 `127.0.0.1`。
- file_sd 默认每 30 秒重新读取 target 文件，正常情况下不需要重启 Prometheus。

检查发现结果：

```bash
curl -fsS http://127.0.0.1:9090/api/v1/targets \
  | python3 -m json.tool
```

也可以在 Prometheus 页面打开 `Status -> Target health`，确认真实 target 为 `UP`。

### 4.3 配置额外 Linux 节点

本机 Node Exporter 已由 `node_exporter` 静态 job 采集。`/etc/prometheus/targets/nodes.yml` 只配置额外的远端 Node Exporter，避免重复采集本机并造成求和类指标偏大。

没有远端节点时：

```yaml
# Managed by my_prometheus install.py
[]
```

存在远端节点时：

```yaml
# Managed by my_prometheus install.py
- targets:
    - 10.20.0.11:9100
    - 10.20.0.12:9100
  labels:
    role: linux
```

## 5. 在网页中查看

### 5.1 SSH 隧道访问

如果服务只监听 `127.0.0.1`，或节点只开放 SSH，在本地电脑执行：

```bash
ssh \
  -L 3000:127.0.0.1:3000 \
  -L 9090:127.0.0.1:9090 \
  -p <SSH端口> \
  <用户>@<服务器地址>
```

保持 SSH 会话运行，然后在本机浏览器打开：

- Grafana：`http://127.0.0.1:3000`
- Prometheus：`http://127.0.0.1:9090`

Grafana 使用用户名 `admin` 和凭据文件中的密码登录。

如果本机端口已占用，可以换成本地端口，例如：

```bash
ssh -L 13000:127.0.0.1:3000 -L 19090:127.0.0.1:9090 \
  -p <SSH端口> <用户>@<服务器地址>
```

此时访问 `http://127.0.0.1:13000` 和 `http://127.0.0.1:19090`。

### 5.2 内网直连

只有服务监听可达地址且安全组、防火墙允许访问时，才能直接打开：

- `http://<节点IP>:3000`
- `http://<节点IP>:9090`

### 5.3 查找 Dashboard

登录 Grafana 后进入 `Dashboards`：

- `Linux Hosts/Linux Node Overview`：Linux CPU、内存、磁盘和网络。
- `SGLang/SGLang PD 合部指标 (SGLang PD Unified Metrics)`：PD 合部指标。
- `SGLang/SGLang PD 分离与 Router 指标 (SGLang PD Disaggregated and Router Metrics)`：Prefill、Decode 和 Router 指标。

PD 分离看板顶部的 `角色 (Role)` 支持单选、多选和 All；`实例 (Instance)`、`模型 (Model)` 也支持多选。

SGLang 面板标题采用 `中文名称（大致解释）`，Prometheus 原始指标名不占用标题或图例，可在面板信息（Panel description）中查看。看板的展示约定如下：

- Counter 原指标虽然以 `_total` 表示累计值，趋势面板统一使用 `rate()` 展示每秒速率，并使用“请求完成速率”“Prefill 吞吐”“Decode 吞吐”等速率名称，不把速率误称为总数。
- Engine 模型级指标严格匹配模型 (Model) 变量，并按 Role、Instance、Model 分组；HTTP、进程等实例级指标不带 `model_name`，不受 Model 变量影响。
- 图例至少显示 Role 和 Instance，模型级 Engine 指标同时显示 Model，选择 All 时可以区分 Prefill、Decode 和不同模型。
- 启动后通常不变化的容量、页大小、上下文长度等配置类指标使用 Stat 数字面板。
- 普通 Histogram 只展示 P95 和平均值，不展示 P80。
- 输入和生成 Token 长度使用分段数量展示；统计窗口是当前选择的 Dashboard 时间范围。
- 未缓存输入 Token 长度不单独展示，页面使用总输入与未缓存输入 Token 计算缓存命中率。
- 每个普通指标单独成图；关键指标和请求全链路时延放在靠前的独立分组中。
- 看板顶部的“采集健康”分组独立展示目标状态、目标缺失状态、最近成功采集距今时间、单次采集样本数和采集耗时。
- 时序图不会跨空值连线；Prometheus 抓取中断会显示为曲线缺口。

输入 Token 分段为 `0-4k`、`4k-15k`、`15k-60k`、`60k-300k`、`300k-1M`、`1M+`；生成 Token 分段为 `0-500`、`500-2k`、`2k-8k`、`8k-30k`、`30k-100k`、`100k+`。这些区间使用 SGLang 默认 Histogram bucket 的实际边界；每段数值由相邻累计 bucket 相减得到，因此不需要修改 SGLang 启动参数。

在 PD 分离与 Router 看板中，所有 PromQL 都直接带有 `role=~"$role"`。选择 Router 后，PD 指标面板不会查询到 PD 数据；由于 Grafana 静态 Dashboard JSON 不支持按变量动态隐藏任意面板，不适用的 PD 面板仍会保留位置并显示 `No data`。

`No data` 不能直接解释为“功能未启用”。先查看“采集健康”分组：`up=0` 表示目标存在但抓取失败；目标缺失状态为 1 表示服务发现、target 配置、标签或变量选择不匹配；最近成功采集距今时间持续增大表示 exporter 或链路已停止成功上报。健康指标正常后，再按以下顺序检查业务指标：

1. 直接检查 `/metrics` 中是否存在面板查询的指标名。
2. 在 Prometheus 中查询 `up` 和具体 `sglang:*` 指标。
3. 检查 target 的 `role` 是否正确。
4. 触发一次真实请求；部分指标只有执行过对应功能后才注册或产生数据。

## 6. 停止、启动与日志

停止默认服务：

```bash
sudo systemctl stop prometheus node_exporter grafana-server
```

停止并取消开机自启：

```bash
sudo systemctl disable --now prometheus node_exporter grafana-server
```

重新启用：

```bash
sudo systemctl enable --now prometheus node_exporter grafana-server
```

查看日志：

```bash
journalctl -u prometheus -u node_exporter -u grafana-server \
  -n 200 --no-pager
```

启用了 Alertmanager 时，在命令中增加 `alertmanager`。

## 7. 卸载

先演练卸载：

```bash
cd /opt/my_prometheus-installer
sudo python3 uninstall.py --yes --dry-run
```

默认卸载服务、二进制和本项目管理的配置，保留监控数据：

```bash
sudo python3 uninstall.py --yes
```

Grafana 在安装前已经存在时默认保留 Grafana 软件包；确认也要删除时：

```bash
sudo python3 uninstall.py --yes --remove-grafana
```

确认不再需要 Prometheus、Grafana 和 Alertmanager 历史数据时：

```bash
sudo python3 uninstall.py --yes --purge-data
```

同时删除安装器添加的防火墙端口规则：

```bash
sudo python3 uninstall.py \
  --yes \
  --purge-data \
  --remove-firewall-rules
```

`--purge-data` 不可恢复，执行前应备份需要保留的数据。卸载器不会删除源码目录 `/opt/my_prometheus-installer`。

## 8. 更新与测试

先更新源码并运行测试：

```bash
cd /opt/my_prometheus-installer
git pull --ff-only
python3 -m unittest discover -s tests -v
```

如果本次只更新 Dashboard，定向发布运行时文件更安全：

```bash
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/node-overview.json \
  /var/lib/grafana/dashboards/linux/node-overview.json
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/sglang-pd-unified.json \
  /var/lib/grafana/dashboards/sglang/sglang-pd-unified.json
sudo install -o grafana -g grafana -m 0644 \
  grafana/dashboards/sglang-pd-disaggregated.json \
  /var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json
```

Grafana provider 会在约 30 秒内重新读取文件。不要为发布 Dashboard 直接使用全局 `--force`：它不仅替换 Dashboard，还会重新生成 `nodes.yml` 和 `sglang-dashboards.yml`，可能覆盖真实 target。需要更新安装器管理的其他系统配置时，先执行 `--dry-run` 并逐项确认影响。
