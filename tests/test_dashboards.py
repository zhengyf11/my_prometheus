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
        cls.operational = {}
        for filename in (
            "sglang-service-overview.json",
            "sglang-pd-pipeline.json",
            "sglang-engine-scheduler.json",
            "sglang-router-worker.json",
            "sglang-kv-capacity.json",
            "sglang-optional-features.json",
        ):
            with open(str(dashboard_dir / filename), "r") as handle:
                cls.operational[filename] = json.load(handle)
        with open(str(grafana_dir / "sglang-translations.json"), "r") as handle:
            cls.translations = json.load(handle)

    def all_panels(self, dashboard):
        result = []

        def visit(panels):
            for panel in panels:
                result.append(panel)
                visit(panel.get("panels", []))

        visit(dashboard["panels"])
        return result

    def data_panels(self, dashboard):
        return [
            panel for panel in self.all_panels(dashboard)
            if panel["type"] not in ("row", "text")
        ]

    def metric_panels(self, dashboard):
        return [
            panel for panel in self.data_panels(dashboard)
            if panel.get("x-panelKind") not in ("scrape-health", "derived")
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
            panel_ids = [panel["id"] for panel in self.all_panels(dashboard)]
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
                for panel in self.all_panels(dashboard)
                for target in panel.get("targets", [])
            ]
            for item in catalog:
                self.assertTrue(
                    any(item["name"] in expression for expression in expressions)
                    or any(
                        panel.get("x-querySource") == "recording-rule"
                        for panel in self.panels_for_metric(dashboard, item["name"])
                    ),
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
            for panel in self.all_panels(dashboard)
            if panel["type"] == "row"
            and panel.get("x-panelKind") not in ("scrape-health", "derived")
        }
        self.assertEqual(set(self.translations["metrics"]), metric_names)
        self.assertEqual(set(self.translations["categories"]), category_names)
        self.assertEqual(len(self.translations["dashboards"]), 8)
        for translation in self.translations["metrics"].values():
            self.assertTrue(translation["title"])
            self.assertTrue(translation["description"])

    def test_dashboards_use_shared_prometheus_datasource(self):
        for dashboard in self.dashboards.values():
            for variable in dashboard["templating"]["list"]:
                self.assertEqual(variable["datasource"]["uid"], "Prometheus")
            for panel in self.all_panels(dashboard):
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
        self.assertIn('expected="true"', definitions["unified"])
        self.assertIn('expected="true"', definitions["split"])

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

        for panel in self.metric_panels(self.dashboards["split"]):
            for target in panel["targets"]:
                self.assertIn('role=~"$role"', target["expr"])
        for panel in self.metric_panels(self.dashboards["unified"]):
            for target in panel["targets"]:
                self.assertIn('role="sglang-unified"', target["expr"])

    def test_engine_model_filters_and_dimensions_are_strict(self):
        instance_metrics = {
            "sglang:http_requests_total",
            "sglang:http_responses_total",
            "sglang:http_requests_active",
            "sglang:routing_keys_active",
            "sglang:process_cpu_seconds_total",
            "sglang:func_latency_seconds",
        }
        for dashboard in self.dashboards.values():
            all_expressions = "\n".join(
                target["expr"]
                for panel in self.data_panels(dashboard)
                for target in panel["targets"]
            )
            self.assertNotIn('$model|^$', all_expressions)

            for item in dashboard["x-metricsCatalog"]:
                metric_name = item["name"]
                if metric_name.startswith(("smg_", "router_")):
                    continue
                panels = self.panels_for_metric(dashboard, metric_name)
                expressions = "\n".join(
                    target["expr"] for panel in panels for target in panel["targets"]
                )
                legends = [
                    target["legendFormat"]
                    for panel in panels
                    for target in panel["targets"]
                ]
                if metric_name in instance_metrics:
                    self.assertNotIn("model_name", expressions, metric_name)
                    self.assertTrue(
                        all("{{model_name}}" not in legend for legend in legends),
                        metric_name,
                    )
                else:
                    self.assertIn('model_name=~"$model"', expressions, metric_name)
                    if not any(
                        panel.get("x-querySource") == "recording-rule"
                        for panel in panels
                    ):
                        self.assertIn("by (role, instance, model_name", expressions, metric_name)
                    self.assertTrue(
                        all("{{model_name}}" in legend for legend in legends),
                        metric_name,
                    )

        for dashboard in self.dashboards.values():
            for panel in self.metric_panels(dashboard):
                for target in panel["targets"]:
                    self.assertIn("{{role}}", target["legendFormat"])
                    self.assertIn("{{instance}}", target["legendFormat"])

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
            for panel in self.all_panels(self.dashboards["unified"])
            if panel["type"] == "row"
            and panel.get("x-panelKind") not in ("scrape-health", "derived")
        }
        split_sections = {
            panel["title"]
            for panel in self.all_panels(self.dashboards["split"])
            if panel["type"] == "row"
            and panel.get("x-panelKind") not in ("scrape-health", "derived")
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

    def test_dashboards_use_short_metric_titles_and_preserve_raw_mapping(self):
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
            for panel in self.metric_panels(dashboard):
                self.assertLessEqual(len(panel["title"]), 24)
                self.assertNotIn("每秒", panel["title"])
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
        allowed_zero_baselines = {
            frozenset(("sglang:num_aborted_requests_total", "sglang:num_requests_total")),
            frozenset(("sglang:num_transfer_failed_reqs_total", "sglang:num_requests_total")),
            frozenset(("sglang:num_bootstrap_failed_reqs_total", "sglang:num_requests_total")),
            frozenset(("sglang:num_prefill_retries_total", "sglang:num_requests_total")),
            frozenset(("smg_router_request_errors_total", "smg_router_requests_total")),
            frozenset(("smg_worker_retries_exhausted_total", "smg_router_requests_total")),
        }
        for dashboard in self.dashboards.values():
            metric_names = [item["name"] for item in dashboard["x-metricsCatalog"]]
            for panel in self.metric_panels(dashboard):
                expressions = "\n".join(target["expr"] for target in panel["targets"])
                if panel.get("x-querySource") == "recording-rule":
                    self.assertTrue(
                        all("my_prometheus:" in target["expr"] for target in panel["targets"])
                    )
                    continue
                matching = {
                    metric for metric in metric_names
                    if re.search(re.escape(metric) + r"(?:_(?:bucket|sum|count))?\{", expressions)
                }
                self.assertTrue(matching)
                self.assertTrue(
                    len(matching) == 1
                    or matching == allowed_calculated_sources
                    or frozenset(matching) in allowed_zero_baselines,
                    "{0}: {1}".format(panel["title"], sorted(matching)),
                )

    def test_dashboards_expose_scrape_health_and_do_not_hide_gaps(self):
        for dashboard in self.dashboards.values():
            health_panels = [
                panel for panel in self.all_panels(dashboard)
                if panel.get("x-panelKind") == "scrape-health"
            ]
            self.assertEqual(len(health_panels), 8)
            expressions = "\n".join(
                target["expr"]
                for panel in health_panels
                for target in panel.get("targets", [])
            )
            self.assertIn("up{", expressions)
            self.assertIn("count(up{", expressions)
            self.assertIn('expected="true"', expressions)
            self.assertIn("max_over_time(timestamp((up{", expressions)
            self.assertIn("scrape_samples_scraped{", expressions)
            self.assertIn("scrape_duration_seconds{", expressions)
            self.assertIn("prometheus_rule_group_rules", expressions)
            self.assertIn("prometheus_rule_evaluation_failures_total", expressions)

            status_panels = [panel for panel in health_panels if panel["type"] == "stat"]
            self.assertEqual(len(status_panels), 5)
            self.assertEqual(
                status_panels[0]["fieldConfig"]["defaults"]["mappings"][0]["options"]["0"]["text"],
                "DOWN",
            )
            freshness = next(
                panel for panel in status_panels
                if panel["title"] == "最近成功采集距今时间"
            )
            self.assertEqual(
                freshness["fieldConfig"]["defaults"]["thresholds"]["steps"],
                [
                    {"color": "green", "value": None},
                    {"color": "yellow", "value": 30},
                    {"color": "red", "value": 60},
                ],
            )

            info = next(panel for panel in self.all_panels(dashboard) if panel["type"] == "text")
            self.assertIn("抓取故障", info["options"]["content"])
            self.assertIn("版本未暴露", info["options"]["content"])

            for panel in self.data_panels(dashboard):
                if panel["type"] == "timeseries":
                    custom = panel["fieldConfig"]["defaults"]["custom"]
                    self.assertFalse(custom["spanNulls"])

    def test_lazy_error_counters_use_zero_baselines(self):
        for dashboard in self.dashboards.values():
            for metric_name in (
                "sglang:num_aborted_requests_total",
                "sglang:num_transfer_failed_reqs_total",
                "sglang:num_bootstrap_failed_reqs_total",
                "sglang:num_prefill_retries_total",
                "smg_router_request_errors_total",
                "smg_worker_retries_exhausted_total",
            ):
                panels = self.panels_for_metric(dashboard, metric_name)
                if not panels:
                    continue
                expression = panels[0]["targets"][0]["expr"]
                self.assertIn(" or ", expression)
                self.assertIn(" * 0", expression)

    def test_counter_panels_are_named_and_documented_as_rates(self):
        expected_titles = {
            "sglang:num_requests_total": "请求完成速率",
            "sglang:prompt_tokens_total": "Prefill 吞吐",
            "sglang:generation_tokens_total": "Decode 吞吐",
        }
        for dashboard in self.dashboards.values():
            for item in dashboard["x-metricsCatalog"]:
                if item["type"] != "counter":
                    continue
                panel = self.panels_for_metric(dashboard, item["name"])[0]
                self.assertNotIn("总数", panel["title"])
                self.assertNotIn("总量", panel["title"])
                if item["name"] == "smg_http_responses_total":
                    self.assertIn("各状态响应速率", panel["description"])
                    self.assertEqual(panel["fieldConfig"]["defaults"]["unit"], "percentunit")
                else:
                    self.assertIn("使用 `rate()` 展示每秒速率", panel["description"])
                self.assertTrue(
                    all("rate(" in target["expr"] for target in panel["targets"])
                )
                if item["name"] in expected_titles:
                    if (
                        item["name"] == "sglang:num_requests_total"
                        and dashboard["uid"] != "my-prometheus-sglang-pd-unified"
                    ):
                        self.assertEqual(
                            panel["title"],
                            "阶段完成速率",
                        )
                        self.assertIn("不是可相加的端到端客户 RPS", panel["description"])
                    else:
                        self.assertEqual(panel["title"], expected_titles[item["name"]])

    def test_split_token_throughput_panels_are_fixed_to_their_stage(self):
        for dashboard in [self.dashboards["split"], *self.operational.values()]:
            for metric_name, fixed_role in (
                ("sglang:prompt_tokens_total", "sglang-prefill"),
                ("sglang:generation_tokens_total", "sglang-decode"),
            ):
                panels = self.panels_for_metric(dashboard, metric_name)
                if not panels:
                    continue
                panel = panels[0]
                expression = panel["targets"][0]["expr"]
                self.assertIn('role=~"$role"', expression)
                self.assertIn('role="{0}"'.format(fixed_role), expression)
                self.assertIn("固定角色", panel["description"])

    def test_recorded_latency_queries_fall_back_to_raw_histograms(self):
        for dashboard in self.dashboards.values():
            for metric_name in (
                "sglang:time_to_first_token_seconds",
                "sglang:inter_token_latency_seconds",
                "sglang:e2e_request_latency_seconds",
            ):
                for target in self.panels_for_metric(dashboard, metric_name)[0]["targets"]:
                    self.assertIn("my_prometheus:", target["expr"])
                    self.assertIn(" or ", target["expr"])
                    self.assertIn(metric_name + "_bucket", target["expr"])

    def test_histograms_use_approved_summary_statistics(self):
        special_histograms = {
            "sglang:prompt_tokens_histogram",
            "sglang:uncached_prompt_tokens_histogram",
            "sglang:generation_tokens_histogram",
        }
        slo_latency_histograms = {
            "sglang:time_to_first_token_seconds",
            "sglang:inter_token_latency_seconds",
            "sglang:e2e_request_latency_seconds",
            "sglang:kv_transfer_latency_ms",
            "smg_http_request_duration_seconds",
            "smg_router_request_duration_seconds",
            "smg_router_ttft_seconds",
            "smg_router_tpot_seconds",
            "smg_router_generation_duration_seconds",
        }
        for dashboard in self.dashboards.values():
            for item in dashboard["x-metricsCatalog"]:
                if item["type"] != "histogram":
                    continue
                name = item["name"]
                matching = [
                    target["expr"]
                    for panel in self.panels_for_metric(dashboard, name)
                    for target in panel["targets"]
                ]
                self.assertFalse(any("histogram_quantile(0.80" in expr for expr in matching))
                if name not in special_histograms:
                    if name in slo_latency_histograms:
                        self.assertTrue(all("my_prometheus:" in expr for expr in matching))
                        self.assertTrue(any("_p50:5m" in expr for expr in matching))
                        self.assertTrue(any("_p95:5m" in expr for expr in matching))
                        self.assertTrue(any("_p99:5m" in expr for expr in matching))
                        self.assertFalse(any(name + "_sum" in expr for expr in matching))
                    else:
                        self.assertTrue(any("histogram_quantile(0.95" in expr for expr in matching))
                        self.assertTrue(any(name + "_sum" in expr for expr in matching))
                        self.assertTrue(any(name + "_count" in expr for expr in matching))

    def test_operations_overviews_cover_engine_and_router_slo_signals(self):
        expected_counts = {
            "关键引擎指标 (Key Engine Metrics)": 15,
            "关键 Router 指标 (Key Router Metrics)": 12,
        }
        split_rows = [
            panel for panel in self.dashboards["split"]["panels"]
            if panel["type"] == "row"
        ]
        business_rows = [
            panel for panel in split_rows if panel.get("x-panelKind") != "scrape-health"
        ]
        self.assertEqual(
            [panel["title"] for panel in business_rows[:2]],
            list(expected_counts),
        )
        for title, expected_count in expected_counts.items():
            row_index = next(
                index for index, panel in enumerate(self.dashboards["split"]["panels"])
                if panel["type"] == "row" and panel["title"] == title
            )
            next_row_index = next(
                (index for index in range(row_index + 1, len(self.dashboards["split"]["panels"]))
                 if self.dashboards["split"]["panels"][index]["type"] == "row"),
                len(self.dashboards["split"]["panels"]),
            )
            panels = self.dashboards["split"]["panels"][row_index + 1:next_row_index]
            self.assertEqual(len(panels), expected_count)
            self.assertTrue(all(panel["gridPos"]["w"] == 8 for panel in panels))

        response_panel = self.panels_for_metric(
            self.dashboards["split"], "smg_http_responses_total"
        )[0]
        self.assertEqual(len(response_panel["targets"]), 3)
        self.assertTrue(all("status_code=~" in target["expr"] for target in response_panel["targets"]))

        health_panel = self.panels_for_metric(
            self.dashboards["split"], "smg_worker_health"
        )[0]
        self.assertEqual(health_panel["type"], "stat")
        self.assertIn("sum by (role, instance)", health_panel["targets"][0]["expr"])

    def test_split_dashboard_exposes_recording_rule_derived_metrics(self):
        dashboard = self.dashboards["split"]
        derived = [
            panel for panel in self.all_panels(dashboard)
            if panel.get("x-panelKind") == "derived"
        ]
        rows = [panel for panel in derived if panel["type"] == "row"]
        data = [panel for panel in derived if panel["type"] != "row"]
        self.assertEqual(
            [panel["title"] for panel in rows],
            [
                "PD 链路派生指标 (PD Pipeline Derived Metrics)",
                "Router 可用性派生指标 (Router Availability Derived Metrics)",
            ],
        )
        self.assertEqual(len(data), 12)
        for panel in data:
            self.assertEqual(len(panel["targets"]), 1)
            self.assertIn("my_prometheus:", panel["targets"][0]["expr"])
            self.assertIn(" or ", panel["targets"][0]["expr"])
            self.assertRegex(panel["targets"][0]["expr"], r"(?:sglang:|smg_)")
            if panel["type"] == "timeseries":
                self.assertFalse(
                    panel["fieldConfig"]["defaults"]["custom"]["spanNulls"]
                )

    def test_operational_dashboards_are_split_and_refresh_by_cost(self):
        expected = {
            "sglang-service-overview.json": ("my-prometheus-sglang-service-overview", "30s"),
            "sglang-pd-pipeline.json": ("my-prometheus-sglang-pd-pipeline", "30s"),
            "sglang-engine-scheduler.json": ("my-prometheus-sglang-engine-scheduler", "1m"),
            "sglang-router-worker.json": ("my-prometheus-sglang-router-worker", "1m"),
            "sglang-kv-capacity.json": ("my-prometheus-sglang-kv-capacity", "1m"),
            "sglang-optional-features.json": ("my-prometheus-sglang-optional-features", "1m"),
        }
        self.assertEqual(set(self.operational), set(expected))
        for filename, dashboard in self.operational.items():
            uid, refresh = expected[filename]
            self.assertEqual(dashboard["uid"], uid)
            self.assertEqual(dashboard["refresh"], refresh)
            panel_ids = [panel["id"] for panel in self.all_panels(dashboard)]
            self.assertEqual(len(panel_ids), len(set(panel_ids)))
            for variable in dashboard["templating"]["list"]:
                self.assertEqual(variable["datasource"]["uid"], "Prometheus")
            for panel in self.data_panels(dashboard):
                self.assertEqual(panel["datasource"]["uid"], "Prometheus")

        self.assertEqual(self.dashboards["unified"]["refresh"], "1m")
        self.assertEqual(self.dashboards["split"]["refresh"], "1m")

        overview = self.operational["sglang-service-overview.json"]
        self.assertEqual(len(self.metric_panels(overview)), 13)
        self.assertEqual(
            len([
                panel for panel in self.all_panels(overview)
                if panel.get("x-panelKind") == "scrape-health"
            ]),
            4,
        )
        self.assertFalse(any(
            panel.get("x-panelKind") == "derived"
            for panel in self.all_panels(overview)
        ))

    def test_full_catalog_dashboards_collapse_non_core_rows_correctly(self):
        expected_expanded = {
            "unified": {"Key Engine Metrics", "Request Latency Pipeline"},
            "split": {"Key Engine Metrics", "Key Router Metrics", "Request Latency Pipeline"},
        }
        for name, dashboard in self.dashboards.items():
            for row in [panel for panel in dashboard["panels"] if panel["type"] == "row"]:
                if row.get("x-panelKind") in ("scrape-health", "derived"):
                    self.assertFalse(row["collapsed"])
                    continue
                original = row["title"].rsplit(" (", 1)[-1].rstrip(")")
                if original in expected_expanded[name]:
                    self.assertFalse(row["collapsed"])
                    self.assertEqual(row["panels"], [])
                else:
                    self.assertTrue(row["collapsed"])
                    self.assertTrue(row["panels"])

    def test_axes_thresholds_and_high_cardinality_tables_are_bounded(self):
        for dashboard in list(self.dashboards.values()) + list(self.operational.values()):
            for panel in self.data_panels(dashboard):
                defaults = panel["fieldConfig"]["defaults"]
                self.assertEqual(defaults["min"], 0)
                if defaults["unit"] == "percentunit":
                    self.assertEqual(defaults["max"], 1)
                for step in defaults.get("thresholds", {}).get("steps", []):
                    self.assertNotEqual(step.get("value"), 80)
                if panel["type"] == "timeseries":
                    calcs = panel["options"]["legend"]["calcs"]
                    self.assertEqual(calcs, ["lastNotNull", "max"])

        for metric_name in (
            "smg_router_request_errors_total",
            "smg_worker_errors_total",
            "smg_worker_retries_exhausted_total",
            "smg_worker_cb_transitions_total",
            "smg_worker_cb_outcomes_total",
        ):
            panel = self.panels_for_metric(self.dashboards["split"], metric_name)[0]
            self.assertEqual(panel["type"], "table")
            self.assertIn("topk(10", panel["targets"][0]["expr"])
            self.assertEqual(panel["targets"][0]["format"], "table")
            self.assertTrue(panel["targets"][0]["instant"])

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
                    [
                        target["legendFormat"].rsplit(" / ", 1)[1]
                        for target in panel["targets"]
                    ],
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
