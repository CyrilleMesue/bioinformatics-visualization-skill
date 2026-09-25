---
name: bioinformatics-visualization
description: >-
  Recommend and generate publication-ready bioinformatics figures from a
  scientific question and a data table. Use when the user asks for a plot,
  figure, heatmap, ROC, Kaplan–Meier curve, PCA, dose-response, enrichment,
  network, or other scientific visualization of biological or clinical data.
---

# Bioinformatics scientific visualization

Follow this sequence. Ask a focused question when a required input is missing.

1. Identify the scientific question.
2. Identify the study design.
3. Inspect the data schema and variable types.
4. Determine whether observations are independent, paired, repeated, nested, censored, spatial, temporal, or networked.
5. Identify the appropriate statistical analysis.
6. Recommend a primary visualization.
7. Recommend companion panels where scientifically useful.
8. Explain the recommendation briefly.
9. Generate the figure with the highest-ranked compatible template.
10. Validate the statistics and the visual encoding.
11. Export the figure, code, plotting data, and audit.

## Routing and safeguards

Read [question_router.md](question_router.md) for the 20 question categories. Read [plot_families.md](plot_families.md) for family and subtype rankings. Read [safeguards.md](safeguards.md) before reporting a p-value, interval, area, or hazard ratio.

Use `bioinformatics_visual_evidence_atlas.visualization.recommend.recommend` with the question, column names, and `milestone_8/template_rankings.json`. Generate with `visualization.figures.render`.

Family and template grades choose a design inside a family. Do not copy a whole-figure score onto every panel. A human grade outranks an assumed grade of 5. A design marked Neither is not a default. Simplified designs are provisional.

## Output

Write SVG, PDF, and 300 dpi PNG, plus plotting data, a config file, a short caption, a statistical audit, and an accessibility check. Use Okabe–Ito colours, bold axis text, a regular-weight legend, and no 3D effects.

## Boundaries

Do not invent statistics. Do not fabricate microscopy, blots, or molecular structures. Do not copy source-paper numbers, labels, or claims into a new figure. See [examples.md](examples.md) and [troubleshooting.md](troubleshooting.md).
