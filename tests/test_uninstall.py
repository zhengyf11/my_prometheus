import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from my_prometheus import uninstall
from my_prometheus.files import MANAGED_MARKER


class UninstallTests(unittest.TestCase):
    def make_context(self, root):
        return SimpleNamespace(
            dry_run=False,
            force=False,
            purge_data=False,
            remove_grafana=False,
            keep_grafana=False,
            remove_firewall_rules=False,
            command_timeout=10,
            proxy=None,
            bin_dir=root / "bin",
            state_dir=root / "state",
            state_file=root / "state/install-state.json",
            systemd_dir=root / "systemd",
            install_dir=root / "install",
            config_dir=root / "config",
            prometheus_data_dir=root / "prometheus-data",
            alertmanager_config_dir=root / "alertmanager-config",
            alertmanager_data_dir=root / "alertmanager-data",
            grafana_data_dir=root / "grafana-data",
            grafana_ini=root / "grafana.ini",
            grafana_provisioning_dir=root / "provisioning",
            grafana_dashboard=root / "node-overview.json",
            dashboard_source=root / "source-dashboard.json",
            prometheus_port=9090,
            grafana_port=3000,
            alertmanager_port=9093,
        )

    def test_remove_managed_file_preserves_unmanaged_content(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            path = Path(temp) / "custom.yml"
            path.write_text("user managed content\n")

            self.assertFalse(uninstall.remove_managed_file(ctx, path))
            self.assertTrue(path.exists())

    def test_remove_managed_file_removes_marked_content(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            path = Path(temp) / "managed.yml"
            path.write_text("# {0}\nvalue: true\n".format(MANAGED_MARKER))

            self.assertTrue(uninstall.remove_managed_file(ctx, path))
            self.assertFalse(path.exists())

    def test_remove_binaries_requires_install_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            ctx.bin_dir.mkdir()
            (ctx.bin_dir / "prometheus").write_text("binary")

            with self.assertRaises(RuntimeError):
                uninstall.remove_binaries(ctx)
            self.assertTrue((ctx.bin_dir / "prometheus").exists())

    def test_remove_binaries_with_state_file(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            ctx.bin_dir.mkdir()
            ctx.state_dir.mkdir()
            (ctx.state_dir / "install-state.json").write_text("{}\n")
            (ctx.bin_dir / "prometheus").write_text("binary")

            uninstall.remove_binaries(ctx)
            self.assertFalse((ctx.bin_dir / "prometheus").exists())

    def test_data_is_preserved_without_purge_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            ctx.prometheus_data_dir.mkdir()

            with mock.patch.object(uninstall, "run") as run:
                uninstall.purge_data(ctx)

            self.assertTrue(ctx.prometheus_data_dir.exists())
            run.assert_not_called()

    def test_stop_services_fails_if_a_service_is_still_active(self):
        ctx = self.make_context(Path("/tmp/test-active-service"))

        def run_result(_ctx, command, **_kwargs):
            if command[:2] == ["systemctl", "is-active"] and command[2] == "prometheus":
                return subprocess.CompletedProcess(command, 0, "active\n", "")
            return subprocess.CompletedProcess(command, 3, "inactive\n", "")

        with mock.patch.object(uninstall, "run", side_effect=run_result):
            with self.assertRaises(RuntimeError):
                uninstall.stop_services(ctx)

    def test_grafana_package_is_removed_when_installer_owned_it(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            ctx.state_dir.mkdir()
            ctx.state_file.write_text('{"grafana_preexisting": false}\n')
            self.assertTrue(uninstall.should_remove_grafana(ctx))

    def test_grafana_package_is_preserved_when_ownership_is_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx = self.make_context(Path(temp))
            self.assertFalse(uninstall.should_remove_grafana(ctx))

    def test_uninstall_stops_services_before_removing_files(self):
        ctx = self.make_context(Path("/tmp/test-uninstall-order"))
        calls = []
        names = (
            "stop_services",
            "remove_binaries",
            "remove_custom_services",
            "remove_prometheus_config",
            "remove_alertmanager_config",
            "remove_grafana_files",
            "remove_grafana_package",
            "remove_grafana_repo",
            "remove_firewall_rules",
            "purge_data",
        )
        patches = [
            mock.patch.object(
                uninstall, name, side_effect=lambda _ctx, name=name: calls.append(name)
            )
            for name in names
        ]
        with patches[0], patches[1], patches[2], patches[3], patches[4], \
                patches[5], patches[6], patches[7], patches[8], patches[9], \
                mock.patch.object(uninstall, "remove_path"):
            uninstall.uninstall(ctx)

        self.assertEqual(calls[0], "stop_services")
        self.assertLess(calls.index("stop_services"), calls.index("remove_binaries"))


if __name__ == "__main__":
    unittest.main()
