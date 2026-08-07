import json
import unittest
from pathlib import Path


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dashboard_dir = Path(__file__).resolve().parent.parent / "grafana/dashboards"
        cls.paths = {
            "unified": dashboard_dir / "sglang-pd-unified.json",
            "split": dashboard_dir / "sglang-pd-disaggregated.json",
        }
        cls.dashboards = {}
        for name, path in cls.paths.items():
            with open(str(path), "r") as handle:
                cls.dashboards[name] = json.load(handle)

    def test_dashboard_has_stable_identity_and_unique_panel_ids(self):
        expected = {
            "unified": "my-prometheus-sglang-pd-unified",
            "split": "my-prometheus-sglang-pd-disaggregated",
        }
        for name, dashboard in self.dashboards.items():
            self.assertEqual(dashboard["uid"], expected[name])
            panel_ids = [panel["id"] for panel in dashboard["panels"]]
            self.assertEqual(len(panel_ids), len(set(panel_ids)))

    def test_dashboards_cover_complete_metric_catalogs(self):
        expected_counts = {"unified": 122, "split": 183}
        for name, dashboard in self.dashboards.items():
            catalog = dashboard["x-metricsCatalog"]
            self.assertEqual(len(catalog), expected_counts[name])
            metric_names = [item["name"] for item in catalog]
            self.assertEqual(len(metric_names), len(set(metric_names)))

            expressions = [
                target["expr"]
                for panel in dashboard["panels"]
                for target in panel.get("targets", [])
            ]
            for item in catalog:
                query_name = (
                    item["name"] + "_bucket"
                    if item["type"] == "histogram"
                    else item["name"]
                )
                self.assertTrue(
                    any(query_name in expression for expression in expressions),
                    "{0} is not queried by {1}".format(item["name"], name),
                )

    def test_dashboards_use_shared_prometheus_datasource(self):
        for dashboard in self.dashboards.values():
            for variable in dashboard["templating"]["list"]:
                self.assertEqual(variable["datasource"]["uid"], "Prometheus")
            for panel in dashboard["panels"]:
                if "datasource" in panel:
                    self.assertEqual(panel["datasource"]["uid"], "Prometheus")
                for target in panel.get("targets", []):
                    self.assertEqual(target["datasource"]["uid"], "Prometheus")

    def test_dashboards_have_role_specific_instance_variables(self):
        definitions = {}
        for name, dashboard in self.dashboards.items():
            instance = next(
                item for item in dashboard["templating"]["list"]
                if item["name"] == "instance"
            )
            definitions[name] = instance["definition"]

        self.assertIn('role="sglang-unified"', definitions["unified"])
        self.assertIn('role=~"$role"', definitions["split"])

        role = next(
            item for item in self.dashboards["split"]["templating"]["list"]
            if item["name"] == "role"
        )
        for expected_role in ("sglang-prefill", "sglang-decode", "sglang-router"):
            self.assertIn(expected_role, role["definition"])
        self.assertFalse(role["multi"])
        self.assertFalse(role["includeAll"])

    def test_engine_dashboards_have_expected_sections(self):
        expected = {
            "HTTP, Process and Functions",
            "Requests, Tokens and User Latency",
            "Scheduler State",
            "KV, SWA and Mamba Pools",
            "CUDA, Tokens and MFU Runtime",
            "Engine Capacity and Startup",
            "Retraction, Queue and Stage Latency",
            "Grammar",
            "Speculative Decoding and Prefill Delayer",
            "PD Queues and KV Transfer",
            "Prefix Cache and Routing Keys",
            "Optional LoRA, HiCache, Streaming and EPLB",
        }
        unified_sections = {
            panel["title"]
            for panel in self.dashboards["unified"]["panels"]
            if panel["type"] == "row"
        }
        split_sections = {
            panel["title"]
            for panel in self.dashboards["split"]["panels"]
            if panel["type"] == "row"
        }
        self.assertEqual(unified_sections, expected)
        self.assertTrue(expected.issubset(split_sections))
        self.assertIn("Router Mesh", split_sections)

    def test_histograms_show_p80_p95_and_mean(self):
        for dashboard in self.dashboards.values():
            expressions = [
                target["expr"]
                for panel in dashboard["panels"]
                for target in panel.get("targets", [])
            ]
            for item in dashboard["x-metricsCatalog"]:
                if item["type"] != "histogram":
                    continue
                name = item["name"]
                matching = [expr for expr in expressions if name in expr]
                self.assertTrue(any("histogram_quantile(0.80" in expr for expr in matching))
                self.assertTrue(any("histogram_quantile(0.95" in expr for expr in matching))
                self.assertTrue(any(name + "_sum" in expr for expr in matching))
                self.assertTrue(any(name + "_count" in expr for expr in matching))

    def test_legacy_sglang_dashboard_is_removed(self):
        self.assertFalse(
            (self.paths["unified"].parent / "sglang-overview.json").exists()
        )
        self.assertFalse(
            (self.paths["unified"].parent / "sglang-router.json").exists()
        )


if __name__ == "__main__":
    unittest.main()
