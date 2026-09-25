---
name: bioinformatics-visualization
description: >-
  Recommend and generate publication-ready bioinformatics figures from a
  scientific question and a data table. Use when the user asks for a plot,
  figure, heatmap, ROC, Kaplan–Meier curve, PCA, dose-response, enrichment,
  network, or other scientific visualization of biological or clinical data.
---

# Bioinformatics scientific visualization

Read [docs/USAGE_GUIDE.md](../../../docs/USAGE_GUIDE.md) for researcher-facing rules. Column contracts are in [docs/DATA_SCHEMAS.md](../../../docs/DATA_SCHEMAS.md). Copy-ready prompts are in [docs/PROMPT_LIBRARY.md](../../../docs/PROMPT_LIBRARY.md).

Do these steps before drawing.

1. Restate the scientific question and the claim the figure must support.
2. State the experimental unit and what one row means.
3. Name the study design: independent, paired, repeated, nested, censored, temporal, or networked.
4. Map columns. If `result_type` mixes AUROC, fold change, hazard ratios, and raw expression in `value`, stop and split the table.
5. List statistics already in the file and statistics the user asked to compute. Compute only what `visualization/stats.py` and the chosen renderer implement.
6. Do not treat a cross-validation fold or a technical replicate as an independent biological replicate.
7. Choose panel mode. `single` means one panel. `auto` proposes the smallest set that answers the primary question, at most four panels unless the user asks for more. `specified` uses only the panels the user named. These modes are instructions to you. They are not arguments of `render`.
8. For a candidate comparison, propose Atlas best, Evidence best, and Compact best on the same rows and the same assumptions. Do not draw them until the user chooses. This workflow is not an implemented function.
9. Call `recommend` with the question, column names, and `milestone_8/template_rankings.json`. Then call `figures.render` or `figures.compose`.
10. If no renderer can do the analysis, say so. Do not imitate the missing plot. Do not pass DESeq2 estimates to `volcano`. Do not call `grouped_bars` a paired test. Do not report a Cox model from `kaplan_meier`.
11. Write PNG at 300 dpi, SVG, PDF, and `audit.json`. `render` also writes `plotting_data.csv` and `caption.txt`. `compose` writes the caption and audit, not the plotting CSV. There is no accessibility-report file. List colour, label, and uncertainty checks in the reply.

`compose` supports panel letters A–H only.

Family grades in the rankings file choose a visual template. They do not validate a statistical test. A human grade outranks an assumed grade of 5. A design marked Neither is not a default.

Read [question_router.md](question_router.md), [plot_families.md](plot_families.md), and [safeguards.md](safeguards.md) before reporting a p-value. Do not invent statistics. Do not fabricate microscopy, blots, or molecular structures. Do not copy source-paper numbers into a new figure.
