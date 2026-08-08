import re
import unittest
from pathlib import Path


class PrometheusRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = (
            Path(__file__).resolve().parent.parent / "templates" / "rules.yml.tpl"
        ).read_text()

    def test_sglang_recording_rules_are_unique_and_complete(self):
        records = re.findall(r"^\s+- record: (\S+)$", self.content, re.MULTILINE)
        self.assertEqual(len(records), len(set(records)))
        self.assertEqual(len(records), 41)
        expected = {
            "my_prometheus:sglang_request_rate:5m",
            "my_prometheus:sglang_ttft_seconds_p50:5m",
            "my_prometheus:sglang_ttft_seconds_p95:5m",
            "my_prometheus:sglang_ttft_seconds_p99:5m",
            "my_prometheus:sglang_itl_seconds_p50:5m",
            "my_prometheus:sglang_itl_seconds_p95:5m",
            "my_prometheus:sglang_itl_seconds_p99:5m",
            "my_prometheus:sglang_e2e_seconds_p50:5m",
            "my_prometheus:sglang_e2e_seconds_p95:5m",
            "my_prometheus:sglang_e2e_seconds_p99:5m",
            "my_prometheus:sglang_router_http_seconds_p99:5m",
            "my_prometheus:sglang_router_request_seconds_p99:5m",
            "my_prometheus:sglang_router_ttft_seconds_p99:5m",
            "my_prometheus:sglang_router_tpot_seconds_p99:5m",
            "my_prometheus:sglang_router_generation_seconds_p99:5m",
            "my_prometheus:sglang_kv_transfer_failure_ratio:5m",
            "my_prometheus:sglang_bootstrap_failure_ratio:5m",
            "my_prometheus:sglang_prefill_retry_ratio:5m",
            "my_prometheus:sglang_prefill_decode_throughput_ratio:5m",
            "my_prometheus:sglang_prefill_decode_worker_capacity_ratio",
            "my_prometheus:sglang_router_error_ratio:5m",
            "my_prometheus:sglang_router_retry_exhausted_ratio:5m",
            "my_prometheus:sglang_router_healthy_workers",
            "my_prometheus:sglang_router_open_circuit_breakers",
            "my_prometheus:sglang_router_worker_load_skew",
        }
        self.assertTrue(expected.issubset(set(records)))

    def test_deterministic_sglang_failure_alerts_are_present(self):
        alerts = set(re.findall(r"^\s+- alert: (\S+)$", self.content, re.MULTILINE))
        self.assertTrue({
            "InstanceDown",
            "SGLangNoHealthyRouterWorkers",
            "SGLangKVTransferFailure",
            "SGLangBootstrapFailure",
            "SGLangRouterRetryExhausted",
            "SGLangWorkerCircuitBreakerOpen",
            "SGLangRouterMeshDisconnected",
        }.issubset(alerts))
        self.assertIn('expr: up{expected!="false"} == 0', self.content)

    def test_rules_do_not_invent_unapproved_slo_thresholds(self):
        for alert_name in (
            "SGLangHighErrorRate",
            "SGLangHighTTFT",
            "SGLangHighE2ELatency",
            "SGLangHighKVCacheUsage",
        ):
            self.assertNotIn("alert: {0}".format(alert_name), self.content)


if __name__ == "__main__":
    unittest.main()
