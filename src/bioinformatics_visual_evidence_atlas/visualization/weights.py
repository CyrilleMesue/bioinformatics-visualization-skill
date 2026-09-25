"""Resolve family/template grades without editing the human export."""

from __future__ import annotations

import csv
import json
from pathlib import Path

FAMILY_RATINGS = (
    "milestone_7/reproduction_quality_review/reviewed/"
    "family_template_ratings_2026-09-24T19-00-23-125Z.csv"
)

FIELDS = [
    "figure_id",
    "panel_ids",
    "plot_family",
    "plot_subtype",
    "template_id",
    "raw_grade",
    "resolved_grade",
    "grade_source",
    "linear_weight",
    "emphasized_weight",
    "blocked_status",
    "simplified_status",
    "preferred_version",
    "preference_strength",
    "human_note",
    "completion_status",
]


def _blank(value: str | None) -> str:
    return (value or "").strip()


def resolve_row(row: dict[str, str]) -> dict:
    completion = _blank(row.get("Completion status"))
    marker = _blank(row.get("Simplified or blocked status"))
    blocked = completion == "blocked" or marker == "blocked"
    simplified = completion == "simplified" or marker == "simplified"
    raw_text = _blank(row.get("Family exemplar grade"))
    raw_grade = int(raw_text) if raw_text else None
    if blocked:
        resolved = None
        source = "blocked"
    elif raw_grade is not None:
        resolved = raw_grade
        source = "human"
    else:
        resolved = 5
        source = "assumed_default"
    linear = None if resolved is None else round(resolved / 10, 4)
    emphasized = None if linear is None else round(linear * linear, 4)
    return {
        "figure_id": row["Figure ID"],
        "panel_ids": row.get("Panel IDs", ""),
        "plot_family": row.get("Plot family", ""),
        "plot_subtype": row.get("Plot subtype", ""),
        "template_id": row.get("Template ID", ""),
        "raw_grade": raw_grade,
        "resolved_grade": resolved,
        "grade_source": source,
        "linear_weight": linear,
        "emphasized_weight": emphasized,
        "blocked_status": "yes" if blocked else "no",
        "simplified_status": "yes" if simplified else "no",
        "preferred_version": _blank(row.get("Preferred family version")),
        "preference_strength": "",
        "human_note": row.get("Family note", ""),
        "completion_status": completion,
    }


def resolve_learning_weights(family_csv: Path) -> list[dict]:
    with family_csv.open(encoding="utf-8", newline="") as handle:
        return [resolve_row(row) for row in csv.DictReader(handle)]


def write_learning_weights(rows: list[dict], csv_path: Path, json_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row[key] is None else row[key] for key in FIELDS})
    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def assert_resolution(rows: list[dict]) -> None:
    if len(rows) != 488:
        raise AssertionError(f"expected 488 family rows, found {len(rows)}")
    graded = [row for row in rows if row["resolved_grade"] is not None]
    blocked = [row for row in rows if row["grade_source"] == "blocked"]
    human = [row for row in rows if row["grade_source"] == "human"]
    assumed = [row for row in rows if row["grade_source"] == "assumed_default"]
    if len(graded) != 481 or len(blocked) != 7 or len(human) != 436 or len(assumed) != 45:
        raise AssertionError(
            f"graded={len(graded)} blocked={len(blocked)} human={len(human)} assumed={len(assumed)}"
        )
    if any(row["resolved_grade"] != row["raw_grade"] for row in human):
        raise AssertionError("a human grade was replaced")
    if any(row["linear_weight"] is not None for row in blocked):
        raise AssertionError("a blocked row received a learning weight")
