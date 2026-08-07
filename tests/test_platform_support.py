import subprocess
import unittest
from pathlib import Path
from unittest import mock

from my_prometheus import command, detect, firewall, grafana, packages


class Context(object):
    package_manager = "apt-get"
    package_index_updated = False
    grafana_version = "latest"
    open_firewall = True
    prometheus_port = 9090
    grafana_port = 3000
    alertmanager_port = 9093
    with_alertmanager = False

    def ensure_grafana_admin_password(self):
        return self.grafana_admin_password


class CommandTests(unittest.TestCase):
    def test_failed_command_redacts_secret(self):
        ctx = Context()
        ctx.dry_run = False
        ctx.proxy = None
        ctx.command_timeout = 10
        failed = subprocess.CompletedProcess([], 1, "", "failed")
        with mock.patch.object(command.subprocess, "run", return_value=failed):
            with self.assertRaises(command.CommandError) as raised:
                command.run(
                    ctx,
                    ["tool", "--password", "secret-value"],
                    secrets=["secret-value"],
                )

        self.assertNotIn("secret-value", str(raised.exception))
        self.assertIn("******", str(raised.exception))


class DetectTests(unittest.TestCase):
    def test_detects_apt_get(self):
        available = {"apt-get": True}
        with mock.patch.object(
            detect, "command_exists", side_effect=lambda name: available.get(name, False)
        ):
            self.assertEqual(detect.detect_package_manager(), "apt-get")

    def test_accepts_ubuntu(self):
        ctx = Context()
        info = {
            "ID": "ubuntu",
            "ID_LIKE": "debian",
            "PRETTY_NAME": "Ubuntu 22.04.5 LTS",
        }
        with mock.patch.object(detect, "read_os_release", return_value=info):
            detect.check_os(ctx)
        self.assertEqual(ctx.os_info, info)


class PackageTests(unittest.TestCase):
    def test_apt_base_packages_update_index_once(self):
        ctx = Context()
        with mock.patch.object(packages, "run") as run:
            packages.ensure_base_packages(ctx)
            packages.ensure_base_packages(ctx)

        commands = [call[0][1] for call in run.call_args_list]
        self.assertEqual(commands.count(["apt-get", "update"]), 1)
        self.assertIn("passwd", commands[1])
        self.assertNotIn("shadow-utils", commands[1])

    def test_detects_installed_deb(self):
        ctx = Context()
        result = subprocess.CompletedProcess([], 0, "install ok installed", "")
        with mock.patch.object(packages, "run", return_value=result) as run:
            self.assertTrue(packages.is_grafana_installed(ctx))
        self.assertEqual(run.call_args[0][1][0], "dpkg-query")

    def test_installs_requested_grafana_deb_version(self):
        ctx = Context()
        ctx.grafana_version = "12.1.0"
        with mock.patch.object(packages, "is_grafana_installed", return_value=False), \
                mock.patch.object(packages, "setup_grafana_apt_repo"), \
                mock.patch.object(packages, "update_package_index"), \
                mock.patch.object(packages, "install_packages") as install:
            packages.install_grafana_package(ctx)
        install.assert_called_once_with(ctx, ["grafana=12.1.0"])


class FirewallTests(unittest.TestCase):
    def test_uses_ufw_when_active(self):
        ctx = Context()
        inactive = subprocess.CompletedProcess([], 3, "inactive\n", "")
        ufw_active = subprocess.CompletedProcess([], 0, "Status: active\n", "")

        def run_result(_ctx, command, **_kwargs):
            if command[:2] == ["ufw", "status"]:
                return ufw_active
            return inactive

        with mock.patch.object(firewall, "command_exists", return_value=True), \
                mock.patch.object(firewall, "run", side_effect=run_result) as run:
            firewall.configure_firewall(ctx)

        commands = [call[0][1] for call in run.call_args_list]
        self.assertIn(["ufw", "allow", "9090/tcp"], commands)
        self.assertIn(["ufw", "allow", "3000/tcp"], commands)
        self.assertNotIn(["ufw", "allow", "9100/tcp"], commands)


class GrafanaTests(unittest.TestCase):
    def test_password_reset_dry_run_does_not_require_installed_cli(self):
        ctx = Context()
        ctx.dry_run = True
        ctx.grafana_admin_password = "test-password"
        with mock.patch.object(grafana, "command_exists") as command_exists:
            grafana.set_admin_password(ctx)
        command_exists.assert_not_called()

    def test_password_reset_prefers_new_cli_with_explicit_paths(self):
        ctx = Context()
        ctx.dry_run = False
        ctx.grafana_admin_password = "test-password"
        with mock.patch.object(grafana, "command_exists", return_value=True), \
                mock.patch.object(grafana, "run") as run:
            grafana.set_admin_password(ctx)

        command = run.call_args[0][1]
        self.assertEqual(command[:2], ["grafana", "cli"])
        self.assertIn("/usr/share/grafana", command)
        self.assertIn("/etc/grafana/grafana.ini", command)
        self.assertEqual(run.call_args[1]["secrets"], ["test-password"])

    def test_provisions_node_and_sglang_dashboards(self):
        ctx = Context()
        ctx.grafana_provisioning_dir = Path("/etc/grafana/provisioning")
        ctx.grafana_dashboard_dir = Path("/var/lib/grafana/dashboards")
        ctx.grafana_assets_dir = Path("/repo/grafana")
        with mock.patch.object(grafana, "write_managed_file") as write, \
                mock.patch.object(grafana, "ensure_dir"), \
                mock.patch.object(grafana, "copy_file") as copy, \
                mock.patch.object(Path, "exists", return_value=True), \
                mock.patch.object(Path, "unlink") as unlink:
            grafana.provision_dashboards(ctx)

        sources = [call[0][1].name for call in copy.call_args_list]
        self.assertEqual(sources, [
            "node-overview.json",
            "sglang-pd-unified.json",
            "sglang-pd-disaggregated.json",
        ])
        destinations = [str(call[0][2]) for call in copy.call_args_list]
        self.assertIn("/var/lib/grafana/dashboards/linux/node-overview.json", destinations)
        self.assertIn("/var/lib/grafana/dashboards/sglang/sglang-pd-disaggregated.json", destinations)
        provider = write.call_args[0][2]
        self.assertIn("folder: Linux Hosts", provider)
        self.assertIn("path: /var/lib/grafana/dashboards/linux", provider)
        self.assertIn("folder: SGLang", provider)
        self.assertIn("path: /var/lib/grafana/dashboards/sglang", provider)
        unlink.assert_called_once()

    def test_provisions_only_shared_prometheus_datasource(self):
        ctx = Context()
        ctx.prometheus_url = "http://localhost:9090"
        ctx.grafana_provisioning_dir = Path("/etc/grafana/provisioning")
        with mock.patch.object(grafana, "write_managed_file") as write:
            grafana.provision_datasource(ctx)

        content = write.call_args[0][2]
        self.assertIn("uid: Prometheus", content)
        self.assertIn("url: http://localhost:9090", content)
        self.assertNotIn("SGLangPlaceholder", content)
        self.assertNotIn("19090", content)


class SGLangTargetTemplateTests(unittest.TestCase):
    def test_defines_placeholder_target_for_each_dashboard_role(self):
        path = Path(__file__).resolve().parent.parent / "templates/sglang-targets.yml.tpl"
        content = path.read_text()

        for role in (
            "sglang-unified",
            "sglang-prefill",
            "sglang-decode",
            "sglang-router",
        ):
            self.assertEqual(content.count("role: {0}".format(role)), 1)
        self.assertEqual(content.count("127.0.0.1:3900"), 4)


if __name__ == "__main__":
    unittest.main()
