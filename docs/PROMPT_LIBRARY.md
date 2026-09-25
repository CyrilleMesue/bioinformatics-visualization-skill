# Prompt library

Copy a prompt into a new Cursor chat after the skill is installed. Placeholders are in angle brackets. Replace them. Do not leave the brackets in the message you send.

Panel mode and candidate mode are **agent-guided**. They are not arguments of `figures.render`.

## Automatic plot selection

Use when you know the question and the table, and you want a plot family chosen from the router.

```text
Primary question: <question>
Intended claim: <claim the figure must support>
Study design: <independent, paired, repeated, nested, censored, temporal, or networked>
Experimental unit: <what one row is>
File: <path>
Columns: <names>
result_type: <name>
Group order: <order>
Statistics already in the table: <list or none>
Statistics to compute only if a renderer does so today: <list>
Panel mode: single
Do not invent a test the renderer does not run.
Synthetic data: <yes or no>
```

## Automatic panel planning

Use when one panel may be too little and you want the smallest set that supports the claim.

```text
Primary question: <question>
Secondary questions that directly support that claim: <list>
File: <path>
One row means: <unit>
Panel mode: auto
Maximum panels: 4
Propose the panel letters before drawing.
Do not add a panel for every column.
Composer limit: 8 panels (A–H). Prefer 4 or fewer.
```

## Three candidate versions

Use before a final export. **Agent-guided.** The library does not build three candidates by itself.

```text
Same file, same group order, same statistical assumptions: <path>
Propose three candidates and do not render until I choose:
1. Atlas best — highest-ranked compatible template in milestone_8/template_rankings.json
2. Evidence best — clearest observations, effects, and uncertainty the current renderers can show
3. Compact best — fewest panels that still answer the primary question
For each: plot family, panel count, encodings, summaries, strengths, limitations, and what is omitted.
```

## Exact user-defined panels

```text
Panel mode: specified
A. <purpose>, renderer <name>, columns <list>, subset <filter>
B. <purpose>, renderer <name>, columns <list>, subset <filter>
Call figures.compose. Do not add panels.
Group order: <order>
```

Implemented renderers: `grouped_bars`, `grouped_boxes`, `correlation_scatter`, `expression_heatmap`, `pca_scatter`, `roc_curve`, `precision_recall`, `calibration`, `kaplan_meier`, `risk_table`, `importance_bars`, `enrichment_dots`, `dose_response`, `network`, `mutation_bars`, `workflow_steps`, `volcano`, `variance_bars`.

## Multi-experiment results

```text
Primary question: <question>
experiment_id values: <list>
Do not pool experiments in one test unless I name the pool.
File: <path>
result_type: <name>
Facet or separate figures by experiment_id.
```

## Multi-dataset validation

```text
Primary question: How does <metric> compare across datasets for each model?
File: <path>
One row is a summary, not a patient.
result_type: external_validation_metric
metric: <AUROC or other>
Map estimate to value and model|dataset to group only for display.
Do not interpret a Welch test on those summaries as a patient-level result.
```

## Multimodal results

```text
Modalities: <list>
File: <path>
Do not place different modalities on one colour scale unless the transform is <named>.
Prefer one panel per modality, maximum 4.
```

## Paired data

```text
Design: paired
subject_id identifies the pair.
File: <path>
Do not call grouped_bars a paired test. stats.paired_t exists and is not used by the bar renderer.
If you cannot show the pairing, say so and stop before claiming a paired p-value.
```

## Repeated measures

```text
Design: repeated measures
subject_id, timepoint, value
One row is one subject at one time, not an independent sample.
The dose_response renderer can show means only if timepoint is mapped to dose, and it ignores subject_id.
```

## Cross-validation

```text
fold identifies a cross-validation fold.
Do not treat folds as biological replicates.
File: <path>
result_type: fold_metric
Show the metric by model and fold. Do not run a t test across folds.
```

## Survival

```text
Primary question: <question>
File: <path>
Columns: time, event, group
event 1 = event, 0 = censored
Renderer: kaplan_meier
The hazard ratio is Mantel–Haenszel for two groups, not a Cox model.
If I need a Cox interval, say the renderer cannot compute it.
```

## Differential expression

```text
I am supplying <DESeq2, edgeR, or limma> results, not raw counts.
Do not pass those estimates to the volcano renderer. It recomputes a Welch test.
Preferred columns: feature, estimate, p_adjusted, comparison
If the current code cannot plot supplied estimates, say so.
```

## Enrichment

```text
File: <path>
Columns: term, neglog10p
These p-values are supplied. Do not recompute them.
Renderer: enrichment_dots
```

## Network

```text
File: <path>
Columns: source, target
Draw only these edges. Weights are ignored by the network renderer.
Do not add edges.
```

## Revision after feedback

```text
Keep the same input rows, group order, and statistical method.
Change only: <layout, labels, panel set, or colours>
Do not recompute a different test.
Previous choice: <candidate name>
Reason for revision: <reason>
```

## Publication-ready export

```text
Render the selected candidate to figures/final/.
Write SVG, PDF, and 300 dpi PNG, plotting_data.csv, caption.txt, and audit.json.
Caption must say the numbers are synthetic if they are.
Do not fabricate microscopy, blots, or molecular structures.
Accessibility: Okabe–Ito palette, readable labels, no 3D.
A separate accessibility report file is not implemented; list the checks in the reply.
```
