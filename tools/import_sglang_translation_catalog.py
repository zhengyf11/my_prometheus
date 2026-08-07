#!/usr/bin/env python3
"""Import reviewed SGLang translations from the Markdown review document."""

import json
from pathlib import Path

from sglang_translation_catalog import CATALOG_PATH


ROOT = Path(__file__).resolve().parent.parent
DOCUMENT_PATH = ROOT / "docs" / "SGLang_Dashboard_中文翻译候选.md"


def table_cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def import_document(path=DOCUMENT_PATH):
    catalog = {"dashboards": {}, "categories": {}, "metrics": {}}
    section = None
    with open(str(path), "r") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if line.startswith("## 1."):
                section = "dashboards"
                continue
            if line.startswith("## 2."):
                section = "categories"
                continue
            if line.startswith("## 3.") or line.startswith("## 4."):
                section = "metrics"
                continue
            if not line.startswith("|") or line.startswith("|---"):
                continue
            cells = table_cells(line)
            if section == "dashboards" and len(cells) == 5 and cells[1] != "当前名称":
                catalog[section][cells[1]] = {
                    "title": cells[2],
                    "description": cells[4],
                }
            elif section == "categories" and len(cells) == 4 and cells[1] != "当前分类":
                catalog[section][cells[1]] = cells[2]
            elif section == "metrics" and len(cells) == 7 and cells[1] != "Prometheus 指标名":
                metric_name = cells[1].strip("`")
                catalog[section][metric_name] = {
                    "title": cells[2],
                    "description": cells[6],
                }
    return catalog


def main():
    catalog = import_document()
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(str(CATALOG_PATH), "w") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        "imported {0} dashboards, {1} categories, and {2} metrics".format(
            len(catalog["dashboards"]),
            len(catalog["categories"]),
            len(catalog["metrics"]),
        )
    )


if __name__ == "__main__":
    main()
