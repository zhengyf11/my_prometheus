# my_prometheus

Python 一键安装部署 Prometheus、Node Exporter 和 Grafana 的工具，面向 CentOS/RHEL 系 systemd 服务器。

## 快速开始

```bash
sudo python3 install.py --yes
```

安装完成后会输出 Prometheus、Grafana 地址和 Grafana 管理员密码。默认会自动生成 Grafana `admin` 用户密码，密码只在安装结束时输出一次。

## 支持环境

- CentOS Stream 8/9、RHEL 8/9 兼容发行版
- Rocky Linux、AlmaLinux、TencentOS 等 `ID_LIKE` 包含 `rhel`、`centos` 或 `fedora` 的系统
- systemd
- Python 3.6+
- x86_64，预留 aarch64 支持

CentOS 7 需要先确保系统存在可用的 `python3`。

## 默认组件

- Prometheus `3.12.0`
- Node Exporter `1.11.1`
- Grafana OSS，默认通过 Grafana 官方 RPM 仓库安装最新版
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
  --listen-address 0.0.0.0 \
  --retention-time 15d \
  --download-timeout 300 \
  --download-retries 3 \
  --command-timeout 600 \
  --with-alertmanager false \
  --open-firewall true
```

支持环境变量，例如：

```bash
export GRAFANA_ADMIN_PASSWORD='change-me'
sudo -E python3 install.py --yes
```

## 默认端口

- Prometheus: `9090`
- Grafana: `3000`
- Node Exporter: `9100`，默认只监听 `127.0.0.1`
- Alertmanager: `9093`，仅启用 `--with-alertmanager true` 时安装

如果 firewalld 正在运行，安装器会默认开放 `9090/tcp` 和 `3000/tcp`。Node Exporter 默认只给本机 Prometheus 抓取，不对外开放。

## 安装后的路径

- Prometheus 配置：`/etc/prometheus/prometheus.yml`
- Prometheus file_sd 目标：`/etc/prometheus/targets/nodes.yml`
- Prometheus 规则：`/etc/prometheus/rules/default.yml`
- Prometheus 数据：`/var/lib/prometheus`
- Grafana dashboard：`/var/lib/grafana/dashboards/node-overview.json`
- 安装状态：`/var/lib/my_prometheus/install-state.json`

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

当前版本暂未实现 `uninstall.py`。需要手动清理时可停止服务后删除对应 systemd unit、二进制、配置和数据目录。生产环境删除 `/var/lib/prometheus` 前请先确认数据不再需要。

## 排障

- Python 版本过低：安装 Python 3.6+ 后执行 `python3 install.py`。
- 端口占用：安装器会检查 `9090`、`9100`、`3000`，已有非本项目进程占用时会退出。
- 外网下载失败：确认服务器能访问 GitHub release 和 `https://rpm.grafana.com`。
- 大文件下载不稳定：可手动把 Prometheus、Node Exporter tar 包或 Grafana RPM 放到 `/opt/my_prometheus/downloads` 后重新执行安装器。
- Grafana 密码遗失：执行 `sudo grafana-cli admin reset-admin-password '<new-password>'`。
- SELinux：安装器不会关闭 SELinux；如遇策略拦截，请结合审计日志单独处理。
