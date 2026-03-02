"""Panel YAML loader (04_VARIANT_PANEL, 09_PLAN task 11)."""

from pathlib import Path

import yaml


def load_panel(panel_path: Path) -> list[dict]:
    """
    Load panel YAML, return list of {variant, expected_class}.
    Supports nested format by mechanism class.
    """
    with open(panel_path) as f:
        data = yaml.safe_load(f) or {}
    entries = []
    for _class, items in data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "variant" in item:
                entries.append({
                    "variant": item["variant"],
                    "expected_class": item.get("expected_class", _class),
                })
            elif isinstance(item, str):
                entries.append({"variant": item, "expected_class": _class})
    return entries
