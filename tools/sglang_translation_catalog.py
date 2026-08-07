"""Load and validate the structured SGLang dashboard translation catalog."""

import json
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parent.parent / "grafana" / "sglang-translations.json"


def load_catalog(path=CATALOG_PATH):
    with open(str(path), "r") as handle:
        catalog = json.load(handle)
    for section in ("dashboards", "categories", "metrics"):
        if section not in catalog or not isinstance(catalog[section], dict):
            raise RuntimeError("translation catalog is missing object: {0}".format(section))
    return catalog


def bilingual(chinese, original):
    return "{0} ({1})".format(chinese, original)


def validate_catalog(catalog, dashboard_names, categories, metric_names):
    expected = {
        "dashboards": set(dashboard_names),
        "categories": set(categories),
        "metrics": set(metric_names),
    }
    errors = []
    for section, expected_names in expected.items():
        actual_names = set(catalog[section])
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        if missing:
            errors.append("{0} missing: {1}".format(section, ", ".join(missing)))
        if extra:
            errors.append("{0} unknown: {1}".format(section, ", ".join(extra)))

    for name, value in catalog["dashboards"].items():
        if not value.get("title") or not value.get("description"):
            errors.append("dashboard translation is incomplete: {0}".format(name))
    for name, value in catalog["categories"].items():
        if not isinstance(value, str) or not value.strip():
            errors.append("category translation is incomplete: {0}".format(name))
    for name, value in catalog["metrics"].items():
        if not value.get("title") or not value.get("description"):
            errors.append("metric translation is incomplete: {0}".format(name))

    if errors:
        raise RuntimeError("invalid translation catalog:\n- " + "\n- ".join(errors))
