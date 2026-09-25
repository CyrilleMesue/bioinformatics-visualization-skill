"""Synthetic two-group figure. Run from the repository root."""

from pathlib import Path

from bioinformatics_visual_evidence_atlas.visualization.figures import render

rows = [
    {"group": "Control", "value": "1.1"},
    {"group": "Control", "value": "0.9"},
    {"group": "Control", "value": "1.2"},
    {"group": "Treated", "value": "1.8"},
    {"group": "Treated", "value": "2.0"},
    {"group": "Treated", "value": "1.7"},
]
out = Path(__file__).resolve().parent / "output"
render("grouped_bars", rows, out, "two_groups", "Treated versus control", True)
print(out / "two_groups.png")
