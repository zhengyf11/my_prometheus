#!/usr/bin/env python3
"""Generate the SGLang translation review document from structured data."""

from pathlib import Path

from generate_sglang_dashboards import ENGINE_GROUPS, ROUTER_GROUPS
from sglang_translation_catalog import load_catalog, validate_catalog


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "SGLang_Dashboard_中文翻译候选.md"

DASHBOARD_SCOPES = {
    "SGLang PD Unified Metrics": "PD 合部",
    "SGLang PD Disaggregated and Router Metrics": "Prefill / Decode / Router",
    "SGLang Service Overview": "Prefill / Decode / Router",
    "SGLang PD Pipeline": "Prefill / Decode",
    "SGLang Engine and Scheduler": "Prefill / Decode",
    "SGLang Router and Worker": "Router",
    "SGLang KV and Capacity": "Prefill / Decode",
    "SGLang Optional Features": "Prefill / Decode / Router",
}

CATEGORY_SCOPES = {}
for name in ENGINE_GROUPS:
    CATEGORY_SCOPES[name] = "Engine"
for name in ROUTER_GROUPS:
    CATEGORY_SCOPES[name] = "Router"

TYPE_NAMES = {
    "counter": "Counter",
    "gauge": "Gauge",
    "histogram": "Histogram",
    "summary": "Summary",
}


def flatten(groups):
    return [item for items in groups.values() for item in items]


def metric_rows(catalog, groups, role_scope):
    rows = []
    for category, items in groups.items():
        for item in items:
            translation = catalog["metrics"][item["name"]]
            rows.append(
                "|  | `{0}` | {1} | {2} | {3} | {4} | {5} |".format(
                    item["name"],
                    translation["title"],
                    TYPE_NAMES[item["type"]],
                    role_scope,
                    catalog["categories"][category],
                    translation["description"],
                )
            )
    return rows


def main():
    catalog = load_catalog()
    engine_items = flatten(ENGINE_GROUPS)
    router_items = flatten(ROUTER_GROUPS)
    validate_catalog(
        catalog,
        DASHBOARD_SCOPES,
        CATEGORY_SCOPES,
        [item["name"] for item in engine_items + router_items],
    )

    lines = [
        "# SGLang Dashboard 中文翻译候选清单",
        "",
        "本文是 Grafana 中文界面使用的翻译目录评审视图。Prometheus 原始指标标识保持不变；Gauge/Histogram 面板标题使用“中文名称（大致解释）”，Counter 趋势面板根据 rate() 查询使用速率名称。原始指标名、累计语义及完整映射保留在面板信息和本清单中。",
        "",
        "## 1. Dashboard 名称",
        "",
        "| 选择 | 当前名称 | 中文候选 | 角色范围 | 简介 |",
        "|---|---|---|---|---|",
    ]
    for name, scope in DASHBOARD_SCOPES.items():
        translation = catalog["dashboards"][name]
        lines.append(
            "|  | {0} | {1} | {2} | {3} |".format(
                name, translation["title"], scope, translation["description"]
            )
        )

    lines.extend([
        "", "## 2. 分类名称", "",
        "| 选择 | 当前分类 | 中文候选 | 所属指标体系 |",
        "|---|---|---|---|",
    ])
    for name, scope in CATEGORY_SCOPES.items():
        lines.append("|  | {0} | {1} | {2} |".format(name, catalog["categories"][name], scope))

    lines.extend([
        "", "## 3. Engine 指标（PD 合部、Prefill、Decode 共用）", "",
        "共 122 个指标族。PD 合部和 PD 分离使用同一套 Collector，实际是否有样本取决于角色、功能开关和运行事件。",
        "", "| 选择 | Prometheus 指标名 | 指标名称中文翻译候选 | 类型 | 角色范围 | 分类候选 | 简介 |",
        "|---|---|---|---|---|---|---|",
    ])
    lines.extend(metric_rows(catalog, ENGINE_GROUPS, "Unified / Prefill / Decode"))

    lines.extend([
        "", "## 4. Router 指标", "",
        "共 61 个指标族，包含 Router 本体和 Router Mesh。",
        "", "| 选择 | Prometheus 指标名 | 指标名称中文翻译候选 | 类型 | 角色范围 | 分类候选 | 简介 |",
        "|---|---|---|---|---|---|---|",
    ])
    lines.extend(metric_rows(catalog, ROUTER_GROUPS, "Router"))
    lines.append("")

    with open(str(OUTPUT), "w") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    main()
