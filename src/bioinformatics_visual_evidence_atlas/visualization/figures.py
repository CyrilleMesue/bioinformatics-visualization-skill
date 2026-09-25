"""Plot construction. Statistics come from the rows passed in."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from matplotlib.patches import FancyBboxPatch

from bioinformatics_visual_evidence_atlas.visualization import stats
from bioinformatics_visual_evidence_atlas.visualization.style import (
    legend,
    new_figure,
    palette,
    save_figure,
    style_axes,
)


def _write_table(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _host(ax, width: float = 7.2, height: float = 4.8):
    if ax is None:
        return new_figure(width, height)
    ax.set_facecolor("white")
    return ax.figure, ax


def _panel_letter(ax, letter: str) -> None:
    ax.text(
        -0.16,
        1.08,
        letter,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        ha="left",
        va="bottom",
        clip_on=False,
    )


def _stars(pvalue: float) -> str:
    if pvalue != pvalue or pvalue >= 0.05:
        return "n.s."
    if pvalue < 0.001:
        return "P < 0.001"
    if pvalue < 0.01:
        return "P < 0.01"
    return "P < 0.05"


def render(renderer: str, rows: list[dict], folder: Path, stem: str, title: str, synthetic: bool) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    _write_table(folder / "plotting_data.csv", rows)
    drawer = RENDERERS[renderer]
    fig, audit = drawer(rows, title)
    paths = save_figure(fig, folder, stem)
    audit.update({"renderer": renderer, "synthetic": synthetic, "n_rows": len(rows), "files": paths})
    (folder / "audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    caption = title
    if synthetic:
        caption += " Values are synthetic demonstration data, not a published result."
    (folder / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    return audit


def _bars(rows, title, ax=None):
    groups = stats.grouped(rows, "value", "group")
    names = list(groups)
    colors = palette(names)
    means, sems = [], []
    for name in names:
        mean, sem = stats.mean_sem(groups[name])
        means.append(mean)
        sems.append(0 if sem != sem else sem)
    fig, ax = _host(ax)
    positions = np.arange(len(names))
    ax.bar(positions, means, color=[colors[name] for name in names], yerr=sems, capsize=4, width=0.7)
    ax.set_xticks(positions, names, rotation=20, ha="right")
    style_axes(ax, title, "Group", "Value")
    pvalue = float("nan")
    if len(names) >= 2:
        _, pvalue = stats.welch(groups[names[0]], groups[names[1]])
        ax.set_title(f"{title}\n{_stars(pvalue)}", fontsize=12, fontweight="bold")
    return fig, {"method": "Mean, SEM, Welch t test for the first two groups", "pvalue": pvalue, "groups": {name: int(len(groups[name])) for name in names}}


def _boxes(rows, title, ax=None):
    groups = stats.grouped(rows, "value", "group")
    names = list(groups)
    colors = palette(names)
    fig, ax = _host(ax)
    drawn = ax.boxplot([groups[name] for name in names], tick_labels=names, patch_artist=True)
    for patch, name in zip(drawn["boxes"], names, strict=True):
        patch.set_facecolor("white")
        patch.set_edgecolor(colors[name])
    style_axes(ax, title, "Group", "Value")
    return fig, {"method": "Quartile boxes. No significance marker is added unless a test is predeclared.", "groups": {name: int(len(groups[name])) for name in names}}


def _scatter(rows, title, ax=None):
    x = np.asarray([float(row["x"]) for row in rows if row.get("x") not in ("", None)])
    y = np.asarray([float(row["y"]) for row in rows if row.get("y") not in ("", None)])
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    coefficient, pvalue = stats.pearson(x, y)
    fig, ax = _host(ax)
    ax.scatter(x, y, c="#0072B2", s=28)
    if stats.finite(coefficient):
        slope, intercept = np.polyfit(x, y, 1)
        grid = np.linspace(x.min(), x.max(), 40)
        ax.plot(grid, slope * grid + intercept, color="#D55E00")
    style_axes(ax, title, "x", "y")
    return fig, {"method": "Pearson correlation", "r": coefficient, "pvalue": pvalue, "n": int(n)}


def _heatmap(rows, title, ax=None):
    features = list(dict.fromkeys(row["feature"] for row in rows))
    samples = list(dict.fromkeys(row["sample"] for row in rows))
    matrix = np.full((len(features), len(samples)), np.nan)
    lookup = {(row["feature"], row["sample"]): float(row["value"]) for row in rows if row.get("value") not in ("", None)}
    for i, feature in enumerate(features):
        for j, sample in enumerate(samples):
            matrix[i, j] = lookup.get((feature, sample), np.nan)
    centered = matrix - np.nanmean(matrix, axis=1, keepdims=True)
    fig, ax = _host(ax, 8, max(4, 0.28 * len(features)))
    image = ax.imshow(np.nan_to_num(centered), aspect="auto", cmap="coolwarm")
    ax.set_xticks(range(len(samples)), samples, rotation=45, ha="right")
    ax.set_yticks(range(len(features)), features)
    style_axes(ax, title, "Sample", "Feature")
    fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02).set_label("Row-centered value")
    return fig, {"method": "Row-centered heatmap. Clustering is not claimed unless a linkage is computed.", "n_features": len(features), "n_samples": len(samples)}


def _pca(rows, title, ax=None):
    features = list(dict.fromkeys(row["feature"] for row in rows))
    samples = list(dict.fromkeys(row["sample"] for row in rows))
    groups = {row["sample"]: row.get("group", "sample") for row in rows}
    matrix = np.zeros((len(samples), len(features)))
    lookup = {(row["sample"], row["feature"]): float(row["value"]) for row in rows}
    for i, sample in enumerate(samples):
        for j, feature in enumerate(features):
            matrix[i, j] = lookup.get((sample, feature), 0.0)
    centered = matrix - matrix.mean(axis=0)
    _u, singular, vt = np.linalg.svd(centered, full_matrices=False)
    scores = centered @ vt[:2].T
    variance = singular**2
    explained = variance / variance.sum()
    fig, ax = _host(ax)
    names = list(dict.fromkeys(groups[sample] for sample in samples))
    colors = palette(names)
    for name in names:
        chosen = [index for index, sample in enumerate(samples) if groups[sample] == name]
        ax.scatter(scores[chosen, 0], scores[chosen, 1], c=colors[name], label=name, s=36)
    legend(ax)
    style_axes(ax, title, f"PC1 ({100 * explained[0]:.1f}% variance)", f"PC2 ({100 * explained[1]:.1f}% variance)")
    return fig, {"method": "PCA by singular value decomposition", "variance_pc1": float(explained[0]), "variance_pc2": float(explained[1])}


def _roc(rows, title, ax=None):
    fig, ax = _host(ax)
    models = list(dict.fromkeys(row.get("model", "model") for row in rows))
    colors = palette(models)
    areas = {}
    for model in models:
        subset = [row for row in rows if row.get("model", "model") == model]
        labels = np.asarray([int(row["label"]) for row in subset])
        scores = np.asarray([float(row["score"]) for row in subset])
        fpr, tpr, area = stats.roc_curve(labels, scores)
        areas[model] = area
        ax.plot(fpr, tpr, color=colors[model], label=f"{model} {area:.2f}" if stats.finite(area) else model)
    ax.plot([0, 1], [0, 1], color="#999999", linestyle="--")
    legend(ax)
    style_axes(ax, title, "False positive rate", "True positive rate")
    return fig, {"method": "ROC from supplied labels and scores", "auc": areas}


def _km(rows, title, ax=None):
    fig, ax = _host(ax)
    groups = list(dict.fromkeys(row["group"] for row in rows))
    colors = palette(groups)
    summary = {}
    for name in groups:
        subset = [row for row in rows if row["group"] == name]
        times = np.asarray([float(row["time"]) for row in subset])
        events = np.asarray([int(row["event"]) for row in subset])
        xs, ys = stats.kaplan_meier(times, events)
        ax.step(xs, ys, where="post", color=colors[name], label=name)
        summary[name] = {"n": len(subset), "events": int(events.sum())}
    if len(groups) == 2:
        a = [row for row in rows if row["group"] == groups[0]]
        b = [row for row in rows if row["group"] == groups[1]]
        _, pvalue = stats.logrank(
            np.asarray([float(row["time"]) for row in a]),
            np.asarray([int(row["event"]) for row in a]),
            np.asarray([float(row["time"]) for row in b]),
            np.asarray([int(row["event"]) for row in b]),
        )
        ratio = stats.hazard_ratio(
            np.asarray([float(row["time"]) for row in a]),
            np.asarray([int(row["event"]) for row in a]),
            np.asarray([float(row["time"]) for row in b]),
            np.asarray([int(row["event"]) for row in b]),
        )
        ax.set_title(f"{title}\nlog-rank {_stars(pvalue)}; HR {ratio:.2f}" if stats.finite(pvalue) else title, fontsize=12, fontweight="bold")
        summary["logrank_p"] = pvalue
        summary["hazard_ratio"] = ratio
    legend(ax)
    style_axes(ax, title if len(groups) != 2 else ax.get_title(), "Time", "Survival probability")
    ax.set_ylim(0, 1.05)
    marks = sorted({float(row["time"]) for row in rows})
    picks = [marks[0], marks[len(marks) // 2], marks[-1]] if marks else []
    risk_lines = []
    for name in groups:
        subset = [row for row in rows if row["group"] == name]
        times = [float(row["time"]) for row in subset]
        risk_lines.append(name + ": " + ", ".join(str(sum(time >= mark for time in times)) for mark in picks))
    if risk_lines:
        ax.text(0.0, -0.22, "Number at risk  " + " | ".join(risk_lines), transform=ax.transAxes, fontsize=8, clip_on=False)
    summary["number_at_risk"] = risk_lines
    return fig, {"method": "Kaplan–Meier, number at risk, two-group log-rank. HR is Mantel–Haenszel.", "groups": summary}


def _importance(rows, title, ax=None):
    ordered = sorted(rows, key=lambda row: float(row["importance"]))
    fig, ax = _host(ax, 7, max(3.5, 0.32 * len(ordered)))
    ax.barh([row["feature"] for row in ordered], [float(row["importance"]) for row in ordered], color="#0072B2")
    style_axes(ax, title, "Importance", "Feature")
    return fig, {"method": "Supplied importance scores. They are not recomputed and are not causal effects."}


def _enrichment(rows, title, ax=None):
    ordered = sorted(rows, key=lambda row: float(row["neglog10p"]))
    fig, ax = _host(ax, 7, max(3.5, 0.32 * len(ordered)))
    ax.scatter([float(row["neglog10p"]) for row in ordered], range(len(ordered)), s=40, c="#0072B2")
    ax.set_yticks(range(len(ordered)), [row["term"] for row in ordered])
    style_axes(ax, title, "-log10 P", "Term")
    return fig, {"method": "Supplied enrichment statistics plotted as dots. P values are not recomputed."}


def _dose(rows, title, ax=None):
    groups = stats.grouped(rows, "value", "dose")
    names = sorted(groups, key=lambda name: float(name))
    means, sems = [], []
    for name in names:
        mean, sem = stats.mean_sem(groups[name])
        means.append(mean)
        sems.append(0 if sem != sem else sem)
    fig, ax = _host(ax)
    ax.errorbar([float(name) for name in names], means, yerr=sems, fmt="-o", color="#0072B2", capsize=3)
    for name in names:
        ax.scatter([float(name)] * len(groups[name]), groups[name], color="#999999", s=12, zorder=0)
    style_axes(ax, title, "Dose", "Response")
    return fig, {"method": "Mean and SEM across doses, with replicate points.", "n_doses": len(names)}


def _network(rows, title, ax=None):
    nodes = list(dict.fromkeys([row["source"] for row in rows] + [row["target"] for row in rows]))
    angles = np.linspace(0, 2 * np.pi, len(nodes), endpoint=False)
    coords = {node: (float(np.cos(angle)), float(np.sin(angle))) for node, angle in zip(nodes, angles, strict=True)}
    fig, ax = _host(ax, 6, 6)
    for row in rows:
        x1, y1 = coords[row["source"]]
        x2, y2 = coords[row["target"]]
        ax.plot([x1, x2], [y1, y2], color="#8A8A8A", linewidth=1)
    for node, (x, y) in coords.items():
        ax.scatter([x], [y], s=80, c="#0072B2", zorder=3)
        ax.text(x * 1.12, y * 1.12, node, ha="center", va="center", fontsize=8)
    ax.set_axis_off()
    ax.set_title(title, fontsize=12, fontweight="bold")
    return fig, {"method": "Edges supplied by the user. No extra edges were added.", "n_edges": len(rows), "n_nodes": len(nodes)}


def _mutation(rows, title, ax=None):
    return _bars(rows, title, ax)


def _workflow(rows, title, ax=None):
    fig, ax = _host(ax, 8, 2.4)
    ax.set_axis_off()
    for index, row in enumerate(rows):
        patch = FancyBboxPatch((index * 1.6, 0.4), 1.4, 0.8, boxstyle="round,pad=0.04", facecolor="#E6F1F8", edgecolor="#0072B2")
        ax.add_patch(patch)
        ax.text(index * 1.6 + 0.7, 0.8, str(row["step"]), ha="center", va="center", fontsize=8)
    ax.set_xlim(-0.2, max(1, len(rows)) * 1.6)
    ax.set_ylim(0, 1.6)
    ax.set_title(title + " (schematic, not a measurement)", fontsize=12, fontweight="bold")
    return fig, {"method": "Text schematic. No statistical claim is made.", "n_steps": len(rows)}


def _calibration(rows, title, ax=None):
    labels = np.asarray([int(row["label"]) for row in rows])
    scores = np.asarray([float(row["score"]) for row in rows])
    edges = np.linspace(0, 1, 6)
    centers, observed, counts = [], [], []
    for left, right in zip(edges[:-1], edges[1:], strict=True):
        chosen = (scores >= left) & (scores < right if right < 1 else scores <= right)
        if not np.any(chosen):
            continue
        centers.append(float(scores[chosen].mean()))
        observed.append(float(labels[chosen].mean()))
        counts.append(int(chosen.sum()))
    fig, ax = _host(ax)
    ax.plot([0, 1], [0, 1], color="#999999", linestyle="--")
    ax.plot(centers, observed, marker="o", color="#0072B2")
    style_axes(ax, title, "Mean predicted score", "Observed frequency")
    return fig, {"method": "Equal-width reliability bins from supplied scores. No probability was invented.", "bins": counts}


def _volcano(rows, title, ax=None):
    features = list(dict.fromkeys(row["feature"] for row in rows))
    groups = list(dict.fromkeys(row["group"] for row in rows))
    xs, ys, labels = [], [], []
    pvalues = []
    for feature in features:
        buckets = stats.grouped([row for row in rows if row["feature"] == feature], "value", "group")
        if len(groups) < 2 or groups[0] not in buckets or groups[1] not in buckets:
            continue
        def _signed_log2(values: np.ndarray) -> float:
            center = float(np.mean(values))
            return float(np.sign(center) * np.log2(abs(center) + 1e-9))

        log_fc = _signed_log2(buckets[groups[1]]) - _signed_log2(buckets[groups[0]])
        _, pvalue = stats.welch(buckets[groups[0]], buckets[groups[1]])
        xs.append(log_fc)
        pvalues.append(pvalue)
        labels.append(feature)
    adjusted = stats.benjamini_hochberg(pvalues)
    ys = [-np.log10(value) if value == value and value > 0 else 0 for value in adjusted]
    fig, ax = _host(ax)
    ax.scatter(xs, ys, c="#0072B2", s=22)
    style_axes(ax, title, "log2 fold change", "-log10 BH-adjusted P")
    return fig, {"method": "Welch t test per feature with Benjamini–Hochberg adjustment", "n_features": len(labels)}


def _pr(rows, title, ax=None):
    fig, ax = _host(ax)
    models = list(dict.fromkeys(row.get("model", "model") for row in rows))
    colors = palette(models)
    areas = {}
    for model in models:
        subset = [row for row in rows if row.get("model", "model") == model]
        labels = np.asarray([int(row["label"]) for row in subset])
        scores = np.asarray([float(row["score"]) for row in subset])
        recall, precision, area = stats.pr_curve(labels, scores)
        areas[model] = area
        ax.plot(recall, precision, color=colors[model], label=f"{model} {area:.2f}" if stats.finite(area) else model)
    legend(ax)
    style_axes(ax, title, "Recall", "Precision")
    return fig, {"method": "Precision-recall from supplied labels and scores", "average_precision": areas}


def _variance_bars(rows, title, ax=None):
    features = list(dict.fromkeys(row["feature"] for row in rows))
    samples = list(dict.fromkeys(row["sample"] for row in rows))
    matrix = np.zeros((len(samples), len(features)))
    lookup = {(row["sample"], row["feature"]): float(row["value"]) for row in rows}
    for i, sample in enumerate(samples):
        for j, feature in enumerate(features):
            matrix[i, j] = lookup.get((sample, feature), 0.0)
    centered = matrix - matrix.mean(axis=0)
    _u, singular, _vt = np.linalg.svd(centered, full_matrices=False)
    variance = singular**2
    explained = 100 * variance / variance.sum()
    shown = min(4, len(explained))
    fig, ax = _host(ax)
    ax.bar([f"PC{i + 1}" for i in range(shown)], explained[:shown], color="#0072B2")
    style_axes(ax, title, "Component", "Variance explained (%)")
    return fig, {"method": "Variance explained by the same PCA", "percent": [float(value) for value in explained[:shown]]}


def _risk_table(rows, title, ax=None):
    groups = list(dict.fromkeys(row["group"] for row in rows))
    times = sorted({float(row["time"]) for row in rows})
    picks = [times[index] for index in range(0, len(times), max(1, len(times) // 4))][:4]
    fig, ax = _host(ax)
    ax.set_axis_off()
    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    cell = [["Group", *[f"{mark:g}" for mark in picks]]]
    for name in groups:
        subset = [float(row["time"]) for row in rows if row["group"] == name]
        cell.append([name, *[str(sum(time >= mark for time in subset)) for mark in picks]])
    table = ax.table(cellText=cell, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)
    return fig, {"method": "Number at risk at selected times", "times": picks}


def compose(panels: list[dict], folder: Path, stem: str, title: str, synthetic: bool) -> dict:
    import matplotlib.pyplot as plt

    count = len(panels)
    cols = 2 if count > 1 else 1
    nrows = int(np.ceil(count / cols))
    fig, axes = plt.subplots(nrows, cols, figsize=(6.6 * cols, 5.0 * nrows), dpi=120, squeeze=False)
    fig.patch.set_facecolor("white")
    flat = axes.ravel()
    audits = []
    for index, panel in enumerate(panels):
        _fig, audit = RENDERERS[panel["renderer"]](panel["rows"], panel["title"], flat[index])
        _panel_letter(flat[index], "ABCDEFGH"[index])
        audits.append({"panel": "ABCDEFGH"[index], "renderer": panel["renderer"], "title": panel["title"], "audit": audit})
    for extra in flat[count:]:
        extra.set_axis_off()
    fig.subplots_adjust(left=0.14, right=0.96, top=0.90, bottom=0.12, wspace=0.55, hspace=0.62)
    folder.mkdir(parents=True, exist_ok=True)
    paths = save_figure(fig, folder, stem)
    caption = title
    if synthetic:
        caption += " Values are synthetic demonstration data, not a published result."
    (folder / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    record = {"renderer": "compose", "panels": audits, "synthetic": synthetic, "files": paths}
    (folder / "audit.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


RENDERERS = {
    "grouped_bars": _bars,
    "grouped_boxes": _boxes,
    "correlation_scatter": _scatter,
    "expression_heatmap": _heatmap,
    "pca_scatter": _pca,
    "roc_curve": _roc,
    "kaplan_meier": _km,
    "importance_bars": _importance,
    "enrichment_dots": _enrichment,
    "dose_response": _dose,
    "network": _network,
    "mutation_bars": _mutation,
    "workflow_steps": _workflow,
    "volcano": _volcano,
    "calibration": _calibration,
    "precision_recall": _pr,
    "variance_bars": _variance_bars,
    "risk_table": _risk_table,
}
