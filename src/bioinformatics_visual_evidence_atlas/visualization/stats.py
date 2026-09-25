"""Statistics computed from the supplied table. Nothing is invented."""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
from scipy import stats


def grouped(rows: list[dict], value: str, group: str) -> dict[str, np.ndarray]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        raw = row.get(value, "")
        if raw in ("", None):
            continue
        buckets[str(row.get(group, ""))].append(float(raw))
    return {key: np.asarray(values, dtype=float) for key, values in buckets.items() if key and len(values)}


def mean_sem(values: np.ndarray) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    if len(values) == 1:
        return float(values[0]), float("nan")
    return float(np.mean(values)), float(stats.sem(values))


def welch(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    if len(a) < 2 or len(b) < 2 or np.std(a) == 0 and np.std(b) == 0:
        return float("nan"), float("nan")
    result = stats.ttest_ind(a, b, equal_var=False)
    return float(result.statistic), float(result.pvalue)


def paired_t(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    if len(a) != len(b) or len(a) < 2:
        return float("nan"), float("nan")
    result = stats.ttest_rel(a, b)
    return float(result.statistic), float(result.pvalue)


def benjamini_hochberg(pvalues: list[float]) -> list[float]:
    usable = [(index, value) for index, value in enumerate(pvalues) if value == value]
    order = sorted(usable, key=lambda item: item[1])
    adjusted = [float("nan")] * len(pvalues)
    running = 1.0
    total = len(order)
    for rank, (index, value) in enumerate(reversed(order), start=1):
        running = min(running, value * total / (total - rank + 1))
        adjusted[index] = min(running, 1.0)
    return adjusted


def pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan"), float("nan")
    result = stats.pearsonr(x, y)
    return float(result.statistic), float(result.pvalue)


def roc_curve(labels: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    from sklearn.metrics import auc
    from sklearn.metrics import roc_curve as sk_roc

    if len(np.unique(labels)) < 2:
        return np.asarray([0.0, 1.0]), np.asarray([0.0, 1.0]), float("nan")
    fpr, tpr, _ = sk_roc(labels, scores)
    return fpr, tpr, float(auc(fpr, tpr))


def pr_curve(labels: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    from sklearn.metrics import average_precision_score, precision_recall_curve

    if len(np.unique(labels)) < 2:
        return np.asarray([0.0, 1.0]), np.asarray([1.0, 0.0]), float("nan")
    precision, recall, _ = precision_recall_curve(labels, scores)
    return recall, precision, float(average_precision_score(labels, scores))


def kaplan_meier(times: np.ndarray, events: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(times)
    times = times[order]
    events = events[order]
    unique = np.unique(times)
    survival = 1.0
    xs = [0.0]
    ys = [1.0]
    for moment in unique:
        at_risk = np.sum(times >= moment)
        deaths = np.sum((times == moment) & (events == 1))
        if at_risk and deaths:
            survival *= 1 - deaths / at_risk
        xs.append(float(moment))
        ys.append(float(survival))
    return np.asarray(xs), np.asarray(ys)


def logrank(time_a, event_a, time_b, event_b) -> tuple[float, float]:
    times = np.unique(np.concatenate([time_a, time_b]))
    observed = 0.0
    expected = 0.0
    variance = 0.0
    for moment in times:
        n1 = np.sum(time_a >= moment)
        n2 = np.sum(time_b >= moment)
        d1 = np.sum((time_a == moment) & (event_a == 1))
        d2 = np.sum((time_b == moment) & (event_b == 1))
        risk = n1 + n2
        deaths = d1 + d2
        if risk <= 1 or deaths == 0:
            continue
        expected_d1 = deaths * n1 / risk
        observed += d1
        expected += expected_d1
        variance += n1 * n2 * deaths * (risk - deaths) / (risk * risk * (risk - 1))
    if variance <= 0:
        return float("nan"), float("nan")
    statistic = (observed - expected) ** 2 / variance
    return float(statistic), float(1 - stats.chi2.cdf(statistic, 1))


def hazard_ratio(time_a, event_a, time_b, event_b) -> float:
    """Mantel-Haenszel odds of death, group B versus group A."""
    times = np.unique(np.concatenate([time_a, time_b]))
    numerator = 0.0
    denominator = 0.0
    for moment in times:
        n1 = np.sum(time_a >= moment)
        n2 = np.sum(time_b >= moment)
        d1 = np.sum((time_a == moment) & (event_a == 1))
        d2 = np.sum((time_b == moment) & (event_b == 1))
        risk = n1 + n2
        if risk == 0:
            continue
        numerator += d2 * n1 / risk
        denominator += d1 * n2 / risk
    if denominator == 0:
        return float("nan")
    return float(numerator / denominator)


def finite(value: float) -> bool:
    return isinstance(value, float) and not math.isnan(value)
