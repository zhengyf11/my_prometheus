import json
import unittest
from pathlib import Path


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = (
            Path(__file__).resolve().parent.parent
            / "grafana/dashboards/sglang-overview.json"
        )
        with open(str(path), "r") as handle:
            cls.dashboard = json.load(handle)

    def test_dashboard_has_stable_identity_and_unique_panel_ids(self):
        self.assertEqual(
            self.dashboard["uid"], "my-prometheus-sglang-overview"
        )
        panel_ids = [panel["id"] for panel in self.dashboard["panels"]]
        self.assertEqual(len(panel_ids), len(set(panel_ids)))

    def test_dashboard_has_expected_operational_sections(self):
        sections = {
            panel["title"]
            for panel in self.dashboard["panels"]
            if panel["type"] == "row"
        }
        expected = {
            "Service Overview",
            "Traffic and Token Throughput",
            "Request Pressure and Queues",
            "Latency",
            "KV Cache and Memory Pools",
            "Runtime Utilization",
            "Speculative Decoding",
            "Engine Capacity and Startup",
        }
        self.assertEqual(sections, expected)

    def test_dashboard_can_filter_instance_and_model(self):
        variables = {
            variable["name"] for variable in self.dashboard["templating"]["list"]
        }
        self.assertEqual(variables, {"instance", "model"})

        expressions = [
            target["expr"]
            for panel in self.dashboard["panels"]
            for target in panel.get("targets", [])
        ]
        self.assertTrue(any("$instance" in expression for expression in expressions))
        self.assertTrue(any("$model" in expression for expression in expressions))


if __name__ == "__main__":
    unittest.main()
