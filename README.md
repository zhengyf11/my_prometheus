# my_prometheus

Python 一键安装部署 Prometheus、Node Exporter 和 Grafana 的工具，面向 Ubuntu、Debian、CentOS/RHEL 系 systemd 服务器。

## 快速开始

```bash
sudo python3 install.py --yes
```

首次安装 Grafana 时，如果没有传入 `--grafana-admin-password`，安装器会自动生成 Grafana `admin` 密码并在安装结束时输出，同时写入 root-only 的 `/var/lib/my_prometheus/grafana-admin-credentials.json` 以便后续健康检查复用。重复执行默认不会重置 Grafana 管理员密码。

## 支持环境

- CentOS Stream 8/9、RHEL 8/9 兼容发行版
- Rocky Linux、AlmaLinux、TencentOS 等 `ID_LIKE` 包含 `rhel`、`centos` 或 `fedora` 的系统
- Ubuntu 20.04/22.04/24.04、Debian 11/12 等使用 APT 和 systemd 的发行版
- systemd
- Python 3.6+
- x86_64，预留 aarch64 支持

CentOS 7 需要先确保系统存在可用的 `python3`。

## 默认组件

- Prometheus `3.12.0`
- Node Exporter `1.11.1`
- Grafana OSS，默认通过 Grafana 官方 RPM 或 APT 仓库安装最新版
- Alertmanager 可选，默认不安装

## 常用参数

```bash
sudo python3 install.py \
  --yes \
  --prometheus-version 3.12.0 \
  --node-exporter-version 1.11.1 \
  --grafana-version latest \
  --grafana-admin-user admin \
  --grafana-admin-password 'change-me' \
  --prometheus-listen-address 0.0.0.0 \
  --node-exporter-listen-address 127.0.0.1 \
  --grafana-listen-address 0.0.0.0 \
  --retention-time 15d \
  --download-timeout 300 \
  --download-retries 3 \
  --command-timeout 600 \
  --install-alertmanager \
  --skip-firewall \
  --proxy http://proxy.example:8080
```

查看安装器版本：

```bash
python3 install.py --version
```

上面的安装命令展示常用参数形态，实际安装时按需选择。

支持环境变量，例如：

```bash
export GRAFANA_ADMIN_PASSWORD='change-me'
sudo -E python3 install.py --yes
```

## 默认端口

- Prometheus: `9090`
- Grafana: `3000`
- Node Exporter: `9100`，默认只监听 `127.0.0.1`
- Alertmanager: `9093`，仅启用 `--with-alertmanager true` 或 `--install-alertmanager` 时安装

如果 firewalld 或 UFW 正在运行，安装器会默认开放 `9090/tcp` 和 `3000/tcp`。Node Exporter 默认只给本机 Prometheus 抓取，不对外开放。

## 监听地址

- `--listen-address` 是兼容参数，作为 Prometheus、Grafana、Alertmanager 的默认监听地址。
- `--prometheus-listen-address` 单独控制 Prometheus。
- `--node-exporter-listen-address` 单独控制 Node Exporter，默认 `127.0.0.1`。
- `--grafana-listen-address` 单独控制 Grafana。
- `--alertmanager-listen-address` 单独控制 Alertmanager。

出于安全默认，Node Exporter 不跟随 `--listen-address` 对外监听；需要远程抓取时显式传入 `--node-exporter-listen-address 0.0.0.0`。

## 校验和代理

Prometheus、Node Exporter、Alertmanager 的 release tarball 默认会校验官方 `sha256sums.txt`。Grafana RPM 会使用官方 RPM metadata 中的 checksum 校验缓存或下载后的 RPM。

离线或受限网络环境可以提供 checksum 文件：

```bash
sudo python3 install.py --yes --checksum-file /path/to/sha256sums.txt
```

如果同时安装 Prometheus、Node Exporter 和 Alertmanager，checksum 文件需要包含所有相关 release asset 的 sha256 行；可以把各组件官方 `sha256sums.txt` 合并到同一个文件。

不建议跳过校验；确需跳过时显式指定：

```bash
sudo python3 install.py --yes --no-verify-checksum
```

HTTP/HTTPS 代理：

```bash
sudo python3 install.py --yes --proxy http://proxy.example:8080
```

`--proxy` 会作用于 Python 下载、Grafana repo metadata 获取，并通过环境变量传给外部命令。若系统包管理器仓库还需要专门的 proxy 配置，请同步配置 yum/dnf/apt。

## Grafana 密码策略

- 首次安装：如果未传 `--grafana-admin-password`，自动生成密码并输出。
- 重复执行：默认不重置 Grafana 管理员密码。
- 显式重置：传入 `--reset-grafana-admin-password`。
- `--grafana-admin-user` 当前只支持 `admin`，传入其他用户名会直接报错。

示例：

```bash
sudo python3 install.py --yes --reset-grafana-admin-password --grafana-admin-password 'new-secret'
```

## 安装后的路径

- Prometheus 配置：`/etc/prometheus/prometheus.yml`
- Prometheus file_sd 目标：`/etc/prometheus/targets/nodes.yml`
- Prometheus 规则：`/etc/prometheus/rules/default.yml`
- Prometheus 数据：`/var/lib/prometheus`
- Grafana dashboard：`/var/lib/grafana/dashboards/node-overview.json`
- 安装状态：`/var/lib/my_prometheus/install-state.json`
- 自动生成的 Grafana 凭据：`/var/lib/my_prometheus/grafana-admin-credentials.json`

## 配置保护

安装器生成的文本配置会带有 `Managed by my_prometheus install.py` 标记。重复执行时：

- 文件不存在：创建。
- 文件存在且带 managed 标记：允许更新并备份。
- 文件存在但不带 managed 标记：默认拒绝覆盖，使用 `--force` 才会备份后替换。
- `/etc/prometheus/targets/nodes.yml` 默认只首次创建，后续保留用户编辑；需要重新生成时使用 `--force`。

## 添加更多主机

在其他 Linux 主机安装 Node Exporter 后，编辑：

```bash
sudo vi /etc/prometheus/targets/nodes.yml
```

示例：

```yaml
- targets:
    - localhost:9100
    - 10.0.0.11:9100
    - 10.0.0.12:9100
  labels:
    role: linux
```

然后重载 Prometheus：

```bash
curl -X POST http://localhost:9090/-/reload
```

如果 reload 失败，可以重启服务：

```bash
sudo systemctl restart prometheus
```

## 查看状态和日志

```bash
systemctl status prometheus node_exporter grafana-server
journalctl -u prometheus -u node_exporter -u grafana-server -f
```

Prometheus targets：

```bash
curl http://localhost:9090/api/v1/targets
```

Grafana health：

```bash
curl http://localhost:3000/api/health
```

## 卸载说明

先演练卸载过程：

```bash
sudo python3 uninstall.py --yes --dry-run
```

默认卸载服务、程序和 managed 配置，但保留监控数据：

```bash
sudo python3 uninstall.py --yes
```

确认不再需要历史数据时再执行彻底清理：

```bash
sudo python3 uninstall.py --yes --purge-data
```

完整的安装、访问、停服、卸载和 03-gpu 运维命令见 [OPERATIONS.md](OPERATIONS.md)。

## 排障

- Python 版本过低：安装 Python 3.6+ 后执行 `python3 install.py`。
- 端口占用：安装器会检查 `9090`、`9100`、`3000`，已有非本项目进程占用时会退出。
- 外网下载失败：确认服务器能访问 GitHub release 和 `https://rpm.grafana.com`。
- 大文件下载不稳定：可手动把 Prometheus、Node Exporter tar 包或 Grafana RPM 放到 `/opt/my_prometheus/downloads` 后重新执行安装器；默认仍会校验 checksum。
- Grafana 密码遗失：执行 `sudo grafana-cli admin reset-admin-password '<new-password>'`。
- SELinux：安装器不会关闭 SELinux；如遇策略拦截，请结合审计日志单独处理。
