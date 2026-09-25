# Data schemas

Compact reference. Explanations are in [USAGE_GUIDE.md](USAGE_GUIDE.md).

Status labels: **implemented** means a renderer reads the column today. **Preferred** means the scientific table you should keep. When they differ, adapt before calling `figures.render`.

## Universal columns

Not every table needs every column. Do not put a different kind of number into `value` without `result_type`.

| Column | Meaning | Type | Role | Common mistake |
| --- | --- | --- | --- | --- |
| experiment_id | One designed comparison or assay run | text | identifies | Reusing one id for unrelated assays |
| dataset | Named data collection | text | stratifies | Treating a dataset as a patient |
| cohort | Recruitment or study group of samples | text | stratifies | Using cohort as a synonym for dataset without defining it |
| result_type | What one row means | text | qualifies | Mixing raw values and AUROC in one `value` column |
| modality | Measurement type (RNA, protein, clinical) | text | stratifies | Stacking modalities on one axis without a transform note |
| analysis | Named statistical procedure | text | qualifies | Hiding DESeq2 vs Welch under one unlabeled column |
| sample_id | Smallest biological sample in the row | text | identifies | Using a well id as a sample when the unit is a mouse |
| subject_id | Person, animal, or paired unit | text | identifies | Omitting it for paired or repeated data |
| group | Condition shown on the axis or in colour | text | stratifies | Encoding group only in the file name |
| comparison | Contrast the row belongs to | text | qualifies | Comparing A vs B with a row that is A vs C |
| feature | Gene, miRNA, protein, or other measured item | text | identifies | Using feature for a model name |
| method | Assay or analytical method | text | stratifies | Calling a model a method and a method a model in the same table |
| model | Named predictor | text | stratifies | One row per patient labeled as a model |
| feature_set | Named set of inputs to a model | text | stratifies | Comparing models that used different genes without saying so |
| metric | Name of the summary (AUROC, F1, RMSE) | text | qualifies | Plotting AUROC and F1 as if they shared a scale |
| value | Number to plot for this result type | number | measures | Mixing fold change and expression in `value` |
| estimate | Supplied effect or metric | number | measures | Recomputing it when the source analysis already supplied it |
| standard_error | Supplied SE | number | measures | Treating SEM from n=1 as known |
| ci_low | Lower confidence limit | number | measures | A percentile labeled as a confidence interval |
| ci_high | Upper confidence limit | number | measures | An interval that excludes the estimate |
| p_value | Supplied p-value | number | measures | A p-value for a different contrast |
| p_adjusted | Supplied multiplicity-adjusted p-value | number | measures | BH-adjusting an already adjusted column again |
| test | Name of the test that produced the row | text | qualifies | Writing “t test” for a paired design |
| timepoint | Time of a repeated measure | number or text | stratifies | Treating time as a dose |
| dose | Dose for a dose-response row | number | stratifies | Unlogged dose stored as text that does not sort numerically |
| event | 1 = event, 0 = censored | integer | measures | Using event=0 to mean “missing” |
| repeat | Technical or biological repeat index | text | identifies | Calling every repeat an independent sample |
| fold | Cross-validation fold id | text | identifies | A t test that treats folds as patients |
| split | Train, validation, or test label | text | stratifies | Reporting training AUROC as external validation |
| batch | Batch or plate | text | stratifies | Colouring by outcome when batch is the confounder |
| replicate | Replicate kind and index | text | qualifies | “replicate” with no biological vs technical label |
| n_samples | Sample size behind a summary row | integer | qualifies | Drawing SEM when n_samples is blank |
| unit | Unit of `value` or `estimate` | text | qualifies | Omitting the unit on a viability percentage |

## Data dictionary

Copy [../data_templates/data_dictionary_template.csv](../data_templates/data_dictionary_template.csv).

| column | meaning | type | unit | role | allowed_values | missing_value_meaning |
| --- | --- | --- | --- | --- | --- | --- |
| field name | what the cell means | number, integer, or text | unit or blank | identifies, stratifies, measures, or qualifies | list, or any | not_applicable or not_available |

A blank cell must be defined. `not_applicable` means the column does not apply to that result type. `not_available` means it should have been measured or calculated and was not. Do not use blank for both.

## Combined versus separate tables

Use one long table when every row is the same kind of observation and `result_type` distinguishes summaries from raw rows. Use separate files when the experimental unit changes. AUROC, log2 fold change, hazard ratio, enrichment score, and raw expression are not interchangeable values.

## Schema catalogue

### A. Independent group comparison

- Preferred columns: `experiment_id`, `sample_id`, `group`, `value`, `unit`. Optional: `batch`, `n_samples`.
- One row: one independent experimental unit.
- Renderer (**implemented**): `grouped_bars` needs `value`, `group`. `grouped_boxes` needs the same. Welch t test compares the first two groups only. `paired_t` exists in `stats.py` and is not called by the bar renderer.
- Router category: Group or condition comparison.
- Error: a paired `subject_id` is ignored by `grouped_bars`.

### B. Paired group comparison

- Preferred columns: `subject_id`, `group`, `value`.
- One row: one subject in one condition.
- Renderer: no paired renderer. Adapter: do not send the table to `grouped_bars` if the claim is paired. **Planned / not yet implemented** as a plotting path. `stats.paired_t` can be called by the agent only when both columns of the pair are aligned.
- Error: Welch on paired rows.

### C. Repeated measures or longitudinal study

- Preferred columns: `subject_id`, `timepoint`, `value`, optional `group`.
- One row: one subject at one time.
- Adapter: `dose_response` reads `dose` and `value`, not `subject_id`. Map `timepoint` to `dose` only for a mean curve, and state that pairing is not modelled.
- Error: treating every timepoint as an independent sample.

### D. Dose-response or time course

- Preferred and renderer columns: `dose`, `value`. Optional `sample_id`.
- One row: one replicate at one dose.
- Renderer (**implemented**): `dose_response`. Mean, SEM, and grey replicate points. No fitted IC50.
- Router category: Temporal or dose-response patterns.

### E. Classification, ROC, and precision-recall

- Preferred columns: `sample_id`, `label`, `score`, `model`, `split`.
- Renderer columns: `label`, `score`, optional `model`.
- One row: one sample score, or one supplied score if `sample_id` is absent. Say which.
- Renderers (**implemented**): `roc_curve`, `precision_recall`.
- Router category: Classification and model performance. `recommend` selects `roc_curve`. The other two are companions the agent must pass to `compose`.

### F. Cross-validation and external validation

- Preferred columns: `model`, `dataset`, `metric`, `estimate`, `fold` or `split`, `result_type`.
- One row: one metric for one model in one dataset or fold. Not one patient.
- Adapter: map `estimate` to `value` and a label such as `model|dataset` to `group` for `grouped_bars`. The Welch test on those rows is usually the wrong test. Tell the agent not to interpret it as a patient-level p-value.
- Error: a t test across folds.

### G. PCA and embeddings

- Preferred columns: `sample_id`, `feature`, `value`, `group`, plus a note of transform and scaling.
- Renderer columns: `feature`, `sample`, `value`, optional `group`. Map `sample_id` to `sample`.
- One row: one feature in one sample.
- Renderer (**implemented**): `pca_scatter` (SVD on column-centred data; blank values become 0). `variance_bars` uses the same columns. UMAP and t-SNE are **not implemented**.
- Router category: Dimensionality reduction and sample separation. Subtype hint `pca`.

### H. Expression or association heatmap

- Preferred columns: `feature`, `sample_id`, `value`.
- Renderer columns: `feature`, `sample`, `value`.
- One row: one feature in one sample.
- Renderer (**implemented**): `expression_heatmap`, row-centred. No clustering claim.
- Router categories: Clustering and molecular subtypes; Multi-omics integration.

### I. Differential expression or abundance

- Preferred columns: `feature`, `estimate` (log2 fold change), `p_adjusted`, `comparison`.
- Renderer columns: `feature`, `value`, `group` on **raw** observations. The volcano recomputes a Welch test and BH adjustment. It does not read a DESeq2 table.
- One preferred row: one feature contrast. One renderer row: one observation of one feature in one group.
- Adapter: do not pass DESeq2 estimates to `volcano`. Plot supplied estimates only if you add a scatter yourself. That supplied-result volcano is **not implemented**.
- Router category: Differential abundance or expression.

### J. Survival

- Preferred columns: `subject_id`, `time`, `event`, `group`. Optional supplied `estimate` and `ci_low`/`ci_high` for a hazard ratio from a Cox model.
- Renderer columns: `time`, `event`, `group`.
- One row: one subject.
- Renderer (**implemented**): `kaplan_meier` (Kaplan–Meier, two-group log-rank, Mantel–Haenszel hazard ratio, number-at-risk text). `risk_table` is a companion. A Cox model is **not implemented**.
- Router category: Survival and time-to-event analysis.

### K. Enrichment

- Preferred and renderer columns: `term`, `neglog10p`. Optional `p_adjusted`, `dataset`.
- One row: one term from a supplied enrichment test.
- Renderer (**implemented**): `enrichment_dots`. P-values are not recomputed.
- Router category: Enrichment and pathway analysis.

### L. Feature importance

- Preferred and renderer columns: `feature`, `importance`. Optional `model`.
- One row: one feature score you supply. Importance is not recomputed and is not causal.
- Renderer (**implemented**): `importance_bars`.
- Router category: Feature importance and model interpretation.

### M. Calibration

- Preferred columns: `label`, `score`, `model`, `split`.
- Renderer columns: `label`, `score`. All rows are pooled into bins.
- One row: one predicted score and observed label.
- Renderer (**implemented**): `calibration`.
- Not selected automatically. The classification route points at `roc_curve`.

### N. Multi-omics

- Preferred columns: `modality`, `feature`, `sample_id`, `value`, `dataset`.
- Renderer columns: `feature`, `sample`, `value` after you confirm one scale.
- One row: one feature in one sample in one modality.
- Error: one heatmap of RNA counts and protein intensities with no transform statement.

### O. Network

- Preferred columns: `source`, `target`, optional `estimate` if the edge has a weight you will not draw.
- Renderer columns: `source`, `target` only. Weights are ignored.
- One row: one supplied edge.
- Renderer (**implemented**): `network`.
- Router category: Network structure and molecular interactions.

### P. Genomic alterations

- Preferred columns: `sample_id`, `feature`, `value` or a count per cohort.
- Renderer columns: `value`, `group` (`mutation_bars` calls `grouped_bars`).
- The question-router text that asks for `sample` is stale. The code requires `value` and `group`.
- Error: a fabricated mutation call.

### Q. Workflow diagrams

- Renderer column: `step`.
- One row: one text step. Not a measurement.
- Renderer (**implemented**): `workflow_steps`.
- Router category: Workflow, architecture, or methodological explanation. Rankings often have no eligible default.

### R. Quality control

- Preferred columns: `sample_id`, `metric`, `value`, `batch`.
- Renderer columns: `value`, `group` for `grouped_boxes`.
- Router category: Data quality and measurement reliability.
- Missing numeric values are dropped, not plotted as zeros, in the bar and box renderers. PCA fills missing feature values with 0.

## Example validation messages

These are the messages to expect from the agent or from `recommend`, not a separate validator CLI.

| Situation | Message |
| --- | --- |
| Bar chart without `value` | `missing_columns` includes `value` |
| ROC without `label` | `missing_columns` includes `label` |
| Paired claim sent to `grouped_bars` | Agent must refuse the paired interpretation; the renderer will still run Welch |
| `result_type` mixes AUROC and expression | Stop. Split the table before rendering |
| More than eight panels in `compose` | Index error. The letters are only A–H |
