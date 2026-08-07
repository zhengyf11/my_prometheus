import json
import re
import unittest
from pathlib import Path


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        grafana_dir = Path(__file__).resolve().parent.parent / "grafana"
        dashboard_dir = grafana_dir / "dashboards"
        cls.paths = {
            "unified": dashboard_dir / "sglang-pd-unified.json",
            "split": dashboard_dir / "sglang-pd-disaggregated.json",
        }
        cls.dashboards = {}
        for name, path in cls.paths.items():
            with open(str(path), "r") as handle:
                cls.dashboards[name] = json.load(handle)
        with open(str(grafana_dir / "sglang-translations.json"), "r") as handle:
            cls.translations = json.load(handle)

    def data_panels(self, dashboard):
        return [
            panel for panel in dashboard["panels"]
            if panel["type"] not in ("row", "text")
        ]

    def panels_for_metric(self, dashboard, metric_name):
        marker = "`{0}`".format(metric_name)
        return [
            panel for panel in self.data_panels(dashboard)
            if marker in panel.get("description", "")
        ]

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
                self.assertTrue(
                    any(item["name"] in expression for expression in expressions),
                    "{0} is not queried by {1}".format(item["name"], name),
                )

    def test_translation_catalog_matches_dashboard_catalogs(self):
        metric_names = {
            item["name"]
            for dashboard in self.dashboards.values()
            for item in dashboard["x-metricsCatalog"]
        }
        category_names = {
            panel["title"].rsplit(" (", 1)[-1].rstrip(")")
            for dashboard in self.dashboards.values()
            for panel in dashboard["panels"]
            if panel["type"] == "row"
        }
        self.assertEqual(set(self.translations["metrics"]), metric_names)
        self.assertEqual(set(self.translations["categories"]), category_names)
        self.assertEqual(len(self.translations["dashboards"]), 2)
        for translation in self.translations["metrics"].values():
            self.assertTrue(translation["title"])
            self.assertTrue(translation["description"])

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
        self.assertTrue(role["multi"])
        self.assertTrue(role["includeAll"])
        self.assertEqual(role["allValue"], ".*")

        split_model = next(
            item for item in self.dashboards["split"]["templating"]["list"]
            if item["name"] == "model"
        )
        unified_model = next(
            item for item in self.dashboards["unified"]["templating"]["list"]
            if item["name"] == "model"
        )
        self.assertIn('role=~"$role"', split_model["definition"])
        self.assertIn('role="sglang-unified"', unified_model["definition"])

        for panel in self.data_panels(self.dashboards["split"]):
            for target in panel["targets"]:
                self.assertIn('role=~"$role"', target["expr"])
        for panel in self.data_panels(self.dashboards["unified"]):
            for target in panel["targets"]:
                self.assertIn('role="sglang-unified"', target["expr"])

    def test_engine_dashboards_have_expected_sections(self):
        original_sections = {
            "Key Engine Metrics",
            "Request Latency Pipeline",
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
        expected = {
            "{0} ({1})".format(self.translations["categories"][name], name)
            for name in original_sections
        }
        self.assertEqual(unified_sections, expected)
        self.assertTrue(expected.issubset(split_sections))
        self.assertIn("关键 Router 指标 (Key Router Metrics)", split_sections)
        self.assertIn(
            "Router 请求全链路时延 (Router Request Latency Pipeline)",
            split_sections,
        )
        self.assertIn("Router Mesh 集群 (Router Mesh)", split_sections)

    def test_dashboards_use_explanatory_metric_titles_and_preserve_raw_mapping(self):
        original_titles = {
            "unified": "SGLang PD Unified Metrics",
            "split": "SGLang PD Disaggregated and Router Metrics",
        }
        for name, dashboard in self.dashboards.items():
            original = original_titles[name]
            translated = self.translations["dashboards"][original]["title"]
            self.assertEqual(dashboard["title"], "{0} ({1})".format(translated, original))

            for variable in dashboard["templating"]["list"]:
                self.assertRegex(variable["label"], r"^.+ \((Role|Instance|Model)\)$")

            metric_names = [item["name"] for item in dashboard["x-metricsCatalog"]]
            for panel in self.data_panels(dashboard):
                self.assertRegex(panel["title"], r"^.+（.+）$")
                for metric_name in metric_names:
                    self.assertNotIn(metric_name, panel["title"])
                    for target in panel["targets"]:
                        self.assertNotIn(metric_name, target["legendFormat"])

            for item in dashboard["x-metricsCatalog"]:
                metric_name = item["name"]
                panels = self.panels_for_metric(dashboard, metric_name)
                self.assertTrue(panels, metric_name)
                translated_metric = self.translations["metrics"][metric_name]
                self.assertTrue(
                    any(translated_metric["description"] in panel["description"] for panel in panels)
                    or metric_name == "sglang:uncached_prompt_tokens_histogram"
                )

    def test_panels_do_not_mix_unrelated_metric_families(self):
        allowed_calculated_sources = {
            "sglang:prompt_tokens_histogram",
            "sglang:uncached_prompt_tokens_histogram",
        }
        for dashboard in self.dashboards.values():
            metric_names = [item["name"] for item in dashboard["x-metricsCatalog"]]
            for panel in self.data_panels(dashboard):
                expressions = "\n".join(target["expr"] for target in panel["targets"])
                matching = {
                    metric for metric in metric_names
                    if re.search(re.escape(metric) + r"(?:_(?:bucket|sum|count))?\{", expressions)
                }
                self.assertTrue(matching)
                self.assertTrue(
                    len(matching) == 1 or matching == allowed_calculated_sources,
                    "{0}: {1}".format(panel["title"], sorted(matching)),
                )

    def test_histograms_show_only_p95_and_mean(self):
        special_histograms = {
            "sglang:prompt_tokens_histogram",
            "sglang:uncached_prompt_tokens_histogram",
            "sglang:generation_tokens_histogram",
        }
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
                self.assertFalse(any("histogram_quantile(0.80" in expr for expr in matching))
                if name not in special_histograms:
                    self.assertTrue(any("histogram_quantile(0.95" in expr for expr in matching))
                    self.assertTrue(any(name + "_sum" in expr for expr in matching))
                    self.assertTrue(any(name + "_count" in expr for expr in matching))

    def test_token_histograms_use_default_sglang_bucket_ranges(self):
        expected = {
            "sglang:prompt_tokens_histogram": {
                "ranges": [
                    "0-4k", "4k-15k", "15k-60k", "60k-300k", "300k-1M", "1M+",
                ],
                "bounds": ["4000", "15000", "60000", "300000", "1000000"],
            },
            "sglang:generation_tokens_histogram": {
                "ranges": [
                    "0-500", "500-2k", "2k-8k", "8k-30k", "30k-100k", "100k+",
                ],
                "bounds": ["500", "2000", "8000", "30000", "100000"],
            },
        }
        for dashboard in self.dashboards.values():
            for metric_name, definition in expected.items():
                panel = self.panels_for_metric(dashboard, metric_name)[0]
                self.assertEqual(panel["type"], "bargauge")
                self.assertEqual(len(panel["targets"]), len(definition["ranges"]))
                self.assertEqual(
                    [target["legendFormat"].split(" ", 1)[1] for target in panel["targets"]],
                    definition["ranges"],
                )
                expressions = "\n".join(target["expr"] for target in panel["targets"])
                self.assertNotIn(r"\+", expressions)
                for bound in definition["bounds"]:
                    self.assertIn(bound, expressions)
                for target in panel["targets"]:
                    self.assertIn("increase(", target["expr"])
                    self.assertIn("round(", target["expr"])
                    self.assertNotIn("histogram_quantile", target["expr"])

    def test_uncached_prompt_distribution_is_replaced_by_cache_hit_rate(self):
        for dashboard in self.dashboards.values():
            panels = self.panels_for_metric(
                dashboard, "sglang:uncached_prompt_tokens_histogram"
            )
            self.assertEqual(len(panels), 1)
            panel = panels[0]
            self.assertEqual(panel["type"], "timeseries")
            self.assertIn("缓存命中率", panel["title"])
            self.assertEqual(panel["fieldConfig"]["defaults"]["unit"], "percentunit")
            self.assertIn("1 - (", panel["targets"][0]["expr"])
            self.assertNotIn("_bucket", panel["targets"][0]["expr"])

    def test_static_metrics_use_stat_panels_and_units_match_metric_semantics(self):
        static_metrics = {
            "sglang:max_total_num_tokens",
            "sglang:max_running_requests_under_SLO",
            "sglang:engine_startup_time",
            "sglang:engine_load_weights_time",
            "sglang:page_size",
            "sglang:num_pages",
            "sglang:context_len",
            "sglang:startup_available_gpu_memory_gb",
            "sglang:spec_num_steps",
            "sglang:spec_num_draft_tokens",
            "sglang:lora_pool_slots_total",
            "sglang:hicache_host_total_tokens",
        }
        expected_units = {
            "sglang:engine_startup_time": "s",
            "sglang:startup_available_gpu_memory_gb": "suffix: GB",
            "sglang:kv_transfer_latency_ms": "ms",
            "sglang:kv_transfer_speed_gb_s": "suffix: GB/s",
            "sglang:token_usage": "percentunit",
            "smg_router_ttft_seconds": "s",
            "router_mesh_bytes_total": "Bps",
        }
        for dashboard in self.dashboards.values():
            catalog_names = {item["name"] for item in dashboard["x-metricsCatalog"]}
            for metric_name, unit in expected_units.items():
                if metric_name not in catalog_names:
                    continue
                panel = self.panels_for_metric(dashboard, metric_name)[0]
                self.assertEqual(panel["fieldConfig"]["defaults"]["unit"], unit)

        for dashboard in self.dashboards.values():
            for metric_name in static_metrics:
                panel = self.panels_for_metric(dashboard, metric_name)[0]
                self.assertEqual(panel["type"], "stat")
                self.assertTrue(panel["targets"][0]["instant"])

    def test_legacy_sglang_dashboard_is_removed(self):
        self.assertFalse(
            (self.paths["unified"].parent / "sglang-overview.json").exists()
        )
        self.assertFalse(
            (self.paths["unified"].parent / "sglang-router.json").exists()
        )


if __name__ == "__main__":
    unittest.main()
