"""Rank templates inside each plot family and subtype."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

PREF_RANK = {
    "Atlas-optimized": 3,
    "Reference-informed": 2,
    "Tie": 1,
    "Neither": 0,
    "": 0,
}

RANK_FIELDS = [
    "plot_family",
    "plot_subtype",
    "template_id",
    "rank",
    "default_eligible",
    "provisional",
    "mean_human_grade",
    "mean_resolved_grade",
    "mean_emphasized_weight",
    "preferred_version_mode",
    "n_rows",
    "n_human",
    "n_assumed",
    "n_question_categories",
    "mean_image_quality",
    "source_figures",
]


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _mode(values: list[str]) -> str:
    if not values:
        return ""
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    return sorted(counts, key=lambda item: (-counts[item], item))[0]


def rank_templates(weights: list[dict], taxonomy_csv: Path) -> list[dict]:
    quality: dict[str, float] = {}
    category: dict[str, str] = {}
    with taxonomy_csv.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            quality[row["figure_id"]] = float(row["image_quality"] or 0)
            category[row["figure_id"]] = row["question_category"]

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in weights:
        if row["grade_source"] == "blocked" or not row["template_id"]:
            continue
        groups[(row["plot_family"], row["plot_subtype"], row["template_id"])].append(row)

    by_subtype: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for (family, subtype, template_id), members in groups.items():
        human = [row["raw_grade"] for row in members if row["grade_source"] == "human"]
        resolved = [row["resolved_grade"] for row in members]
        emphasized = [row["emphasized_weight"] for row in members]
        prefs = [row["preferred_version"] for row in members if row["preferred_version"]]
        mode = _mode(prefs)
        simplified = sum(row["simplified_status"] == "yes" for row in members) / len(members)
        categories = {category[row["figure_id"]] for row in members if row["figure_id"] in category}
        images = [quality[row["figure_id"]] for row in members if row["figure_id"] in quality]
        provisional = simplified >= 0.5
        eligible = mode != "Neither" and not provisional
        by_subtype[(family, subtype)].append(
            {
                "plot_family": family,
                "plot_subtype": subtype,
                "template_id": template_id,
                "default_eligible": "yes" if eligible else "no",
                "provisional": "yes" if provisional else "no",
                "mean_human_grade": _mean([float(value) for value in human]),
                "mean_resolved_grade": _mean([float(value) for value in resolved]),
                "mean_emphasized_weight": _mean([float(value) for value in emphasized]),
                "preferred_version_mode": mode,
                "n_rows": len(members),
                "n_human": len(human),
                "n_assumed": sum(row["grade_source"] == "assumed_default" for row in members),
                "n_question_categories": len(categories),
                "mean_image_quality": _mean(images),
                "source_figures": sorted({row["figure_id"] for row in members}),
                "_human": _mean([float(value) for value in human]) if human else -1,
                "_resolved": _mean([float(value) for value in resolved]) or 0,
                "_pref": PREF_RANK.get(mode, 0),
                "_access": 1 if mode in {"Atlas-optimized", "Tie"} else 0,
                "_complete": 0 if provisional else 1,
                "_image": _mean(images) or 0,
            }
        )

    ranked: list[dict] = []
    for key in sorted(by_subtype):
        candidates = sorted(
            by_subtype[key],
            key=lambda item: (
                item["_human"],
                item["_resolved"],
                item["_pref"],
                item["n_question_categories"],
                item["_complete"],
                item["_access"],
                item["_image"],
                item["template_id"],
            ),
            reverse=True,
        )
        for index, item in enumerate(candidates, start=1):
            item["rank"] = index
            ranked.append({field: item[field] for field in RANK_FIELDS})
    return ranked


def write_rankings(rows: list[dict], csv_path: Path, json_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RANK_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "source_figures": " | ".join(row["source_figures"])})
    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
