# Usage guide

This guide is for a researcher who knows the study and is opening this repository for the first time. It does not assume you know the Python layout.

Labels used below:

- **Implemented:** the current Python code does this.
- **Agent-guided:** Cursor is instructed to do this. There is no function that does it for you.
- **Recommended workflow:** a way to ask for the work. Not a library flag.
- **Planned / not yet implemented:** neither the code nor a safe agent workaround does this.

Start with [QUICK_START.md](QUICK_START.md) if you want the short path. Column tables are in [DATA_SCHEMAS.md](DATA_SCHEMAS.md). Prompts are in [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md).

## 1. Overview

The skill helps you turn a scientific question and a tidy table into a figure. It recommends a plot family, chooses a ranked template inside that family, and can draw a fixed set of chart types.

It does not search papers, download data, or run a full analysis pipeline. It does not decide that a statistical method is valid because an atlas figure scored highly. Rankings in `milestone_8/template_rankings.json` record human grades of **visual templates**. They are not evidence that Welch’s t test, a Mantel–Haenszel hazard ratio, or any other test fits your study.

**Implemented outputs** from `figures.render` and `figures.compose`:

- PNG at 300 dpi, SVG, and PDF
- `plotting_data.csv`
- `caption.txt` (the title, plus a synthetic-data sentence when you set that flag)
- `audit.json` (method name and the numbers that renderer computed)

**Not implemented as files:** a standalone plotting script, a figure-specification format, and an accessibility report. Those are **agent-guided**: ask the agent to write the script and to list the accessibility checks in the reply.

`recommend` returns a category, a renderer name, missing columns, and a template id. It does not draw. The agent must call `render` or `compose`.

## 2. Installation and project setup

```bash
git clone https://github.com/CyrilleMesue/bioinformatics-visualization-skill.git
cd bioinformatics-visualization-skill
python -m pip install -r requirements.txt
export PYTHONPATH=src
python -c "from bioinformatics_visual_evidence_atlas.visualization import recommend; print('ok')"
PYTHONPATH=src python examples/plot_two_groups.py
```

Editable install is **not documented as supported**. `pyproject.toml` has no `[build-system]` table. Use `PYTHONPATH=src`.

Copy the skill into the project where you chat:

```bash
mkdir -p /path/to/your-project/.cursor/skills
cp -a .cursor/skills/bioinformatics-visualization /path/to/your-project/.cursor/skills/
```

Open a **new** Cursor chat in that project. In the first message, give the path to this repository so the agent can import `src` and read `milestone_8/template_rankings.json`.

Recommended layout for the scientific project (this is a **recommended workflow**, not created by the installer):

```text
project/
├── .cursor/skills/bioinformatics-visualization/
├── data/raw/          # files as received
├── data/processed/    # tidy tables ready to plot
├── data/metadata/     # data dictionaries
├── analysis/preprocessing/
├── analysis/statistics/
├── figure_requests/   # YAML requests
├── figures/previews/
├── figures/final/
├── scripts/
└── README.md
```

`data/raw` stays untouched. `data/processed` holds the long tables. `analysis/` is where DESeq2, cross-validation, or a Cox model lives if this library cannot run it. `figure_requests/` records what you asked. `figures/previews` are for comparison. `figures/final` is the version you keep. `scripts/` holds the Python the agent writes so the figure can be redrawn.

## 3. Minimum input requirements

Every request should name:

1. The principal scientific question.
2. The claim the figure must support.
3. The experimental unit (what one row is).
4. The study design.
5. The file or files.
6. The column mapping.
7. Group order.
8. Statistics already in the table.
9. Statistics you still want, and whether the current renderer can compute them.
10. Output paths and formats.
11. Constraints (do not pool cohorts, do not draw a blot, and so on).

Insufficient: “Plot the RNA-seq.”

Well specified: “Primary question: which of two synthetic treatments changes the viability readout? One row is one independent well. File `data/processed/viability.csv`. Columns `group`, `value`. Order Control, DrugA. Panel mode single. Welch is acceptable. Write `figures/previews/viability`.”

## 4. Tidy-data principles

Tidy long format means three rules.

- One variable per column.
- One observation per row.
- The experimental unit is a column, not a filename.

| Term | Meaning |
| --- | --- |
| Subject or biological sample | The person, animal, or specimen you infer to |
| Biological replicate | An independent subject or sample |
| Technical replicate | A repeated measurement of the same sample |
| Repeated measurement | The same subject observed again over time or condition |
| Cross-validation fold | A partition of samples used to score a model |
| Resampling repeat | A bootstrap or similar redraw |
| Dataset or cohort | A named collection of samples. Say which word you mean |
| Analytical experiment | One designed comparison, identified by `experiment_id` |
| Feature | A gene, protein, or other measured item |
| Model or method | A predictor, or the assay/algorithm that produced a column |
| Metric | AUROC, F1, and similar summaries |
| Statistical comparison | The contrast a p-value or estimate refers to |

A fold is not a patient. A technical replicate is not a biological replicate. Do not hand those rows to a test that assumes independent subjects.

## 5. Recommended universal columns

The full table is in [DATA_SCHEMAS.md](DATA_SCHEMAS.md). You do not need every column. You do need the columns the chosen renderer reads, listed in that file.

## 6. Data dictionary

Use [../data_templates/data_dictionary_template.csv](../data_templates/data_dictionary_template.csv).

Each blank must mean either `not_applicable` or `not_available`. An undefined blank is how a missing expression value becomes a fake zero in PCA. The PCA renderer fills a missing `value` with 0. Bar and box renderers drop blank `value` cells instead. Those two behaviours differ. State the policy in the request.

## 7. Managing multiple result types

One combined table is appropriate when `result_type` is filled and you filter to one type before plotting. Separate files are safer when the unit changes (a patient versus a gene versus a model-fold summary).

Example `result_type` values: `raw_observation`, `group_summary`, `fold_metric`, `external_validation_metric`, `differential_feature`, `survival_effect`, `enrichment_term`, `network_edge`, `calibration_bin`.

AUROC, log2 fold change, a hazard ratio, an enrichment score, and a raw expression value must not share `value` without `result_type`. Filtering is **agent-guided**. No renderer filters on `result_type` by itself.

## 8. Analysis-specific schemas

Details, CSV shapes, and renderer mismatches are in [DATA_SCHEMAS.md](DATA_SCHEMAS.md) sections A–R. Read that page before you rename columns. The important mismatches are:

- Paired tests are not what `grouped_bars` runs.
- Differential-expression volcano recomputes Welch tests. It does not read DESeq2 output.
- PCA centres columns and fills blanks with 0. It does not scale, and it does not run UMAP.
- Cross-validation summaries are not independent biological replicates.
- Survival hazard ratios from `kaplan_meier` are Mantel–Haenszel, not Cox models.
- Network weights are ignored.

## 9. Statistical safeguards

The agent must follow [../.cursor/skills/bioinformatics-visualization/safeguards.md](../.cursor/skills/bioinformatics-visualization/safeguards.md).

- Do not invent a p-value, interval, area, or hazard ratio.
- Do not silently swap a paired test for Welch, or the reverse.
- Do not treat a blank as zero unless the renderer does so and you have said that is acceptable. PCA does this. Bars do not.
- Do not pool cohorts, modalities, metrics, or experiments unless the request names the pool.
- If the table already contains DESeq2, edgeR, or limma estimates, do not recompute them with the Welch volcano.
- If publication-grade survival inference needs a Cox interval, say this library cannot compute it.
- Folds are dependent. Do not t-test them as if they were patients.

**Implemented calculations:** mean and SEM, Welch t test on the first two groups, Benjamini–Hochberg inside the volcano only, Pearson correlation, ROC and average precision, equal-width calibration bins, Kaplan–Meier, two-group log-rank, Mantel–Haenszel hazard ratio, SVD for PCA. `stats.paired_t` exists and no renderer calls it.

## 10. Scientific-question hierarchy

Write one primary question. That question chooses the principal panel. A secondary question becomes a companion panel only when it supports the same claim. Otherwise make another figure.

Multi-cohort classification: primary panel is external AUROC by model and dataset. A ROC on one held-out cohort is a companion only if that cohort is part of the claim. A gene heatmap is a different figure.

Treatment experiment: primary panel is the viability contrast. A dose curve is a second figure unless the claim is the dose trend.

Multi-omics biomarker: primary panel is the validation metric. An RNA heatmap and a protein heatmap are companions only when they show the same samples and the same claim. Do not mix their scales.

## 11. Panel-planning policy

**Recommended workflow**, **agent-guided**:

| Mode | Meaning |
| --- | --- |
| single | Exactly one analytical panel |
| auto | The agent proposes the smallest set that answers the primary question |
| specified | You name the panels |

Priority: your written requirements, then the evidence the claim needs, then the study design, then atlas composition habits. Auto mode must not make one panel per column. Group or facet when that preserves the unit.

Before a complex figure, the agent should list, for each panel: letter, purpose, data subset, plot family, statistical content, and link to the primary question.

Default maximum: 4 analytical panels. More only with a reason you accept. **Implemented limit:** `compose` labels panels A–H only. A ninth panel raises an error. There is no `maximum_panels` argument in code.

## 12. Candidate-design workflow

**Agent-guided.** Not an implemented function.

Using the same rows, the same group order, and the same statistical assumptions, the agent may propose up to three structurally different options:

1. Atlas best: the highest-ranked compatible row in `milestone_8/template_rankings.json`.
2. Evidence best: the current renderer that shows observations, effects, and uncertainty most directly.
3. Compact best: the fewest panels that still answer the primary question.

Colour changes alone are not three candidates. For each option record plot family, panel count, encodings, summaries, strengths, limitations, and what is omitted. Draw only after you choose.

## 13. Prompt templates

Use [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md). The eight situations in the milestone (minimal, publication, multi-dataset, candidates, explicit panels, automatic panel count, revision, and regenerate-without-new-statistics) are all in that file.

## 14. Worked examples

All numbers below are **synthetic**. They are not biological findings.

### MTT dose response

Question: how does synthetic viability change across six doses? Design: independent replicates at each dose. One row: one well at one dose. Columns: `dose`, `value`. Renderer: `dose_response` (**implemented**). Prompt: the dose-response template in [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md). Caution: no IC50 is fitted. Example rows are in `data_templates/` only for the long tables listed there; put dose rows in a project CSV with those two columns.

### Paired RT-qPCR

Question: did the synthetic post measurement change within animal? Design: paired. Columns: `subject_id`, `group`, `value`. **Not implemented** as a paired figure. Do not accept a Welch bar chart as the paired result.

### AD versus control, several cohorts

Question: do synthetic AD and control scores separate, and does that hold in each dataset? PCA renderer needs `feature`, `sample`, `value`. A cohort column is not read unless you map it to `group`. State the scaling policy. PCA will fill blanks with 0.

### Models across cross-validation and leave-one-cohort-out

Question: which synthetic model has the higher external AUROC? One row: one model, one dataset, one metric. `result_type` is `fold_metric` or `external_validation_metric`. Map to `value` and `group` only for display. Do not t-test folds.

### Differential expression

If the numbers are DESeq2 estimates, do not use `volcano`. That renderer recomputes Welch tests from raw `feature`, `value`, `group` rows.

### Survival

Columns `time`, `event`, `group`. Renderer `kaplan_meier` plus companion `risk_table`. The printed hazard ratio is Mantel–Haenszel for two groups.

### Multi-omics biomarker

Keep RNA and protein in separate panels or separate files unless you name the transform. Heatmap columns are `feature`, `sample`, `value`.

### Enrichment

Columns `term`, `neglog10p`. The dot plot does not recompute p-values.

## 15. Output contract

| Artifact | Status |
| --- | --- |
| SVG, PDF, 300 dpi PNG | Implemented by `save_figure` |
| Plot-ready data `plotting_data.csv` | Implemented by `render` only. `compose` does not write that CSV |
| Caption `caption.txt` | Implemented |
| Statistical audit `audit.json` | Implemented. Contains the method string and computed numbers for that renderer |
| Configuration file | Not implemented. Put the YAML request in `figure_requests/` yourself |
| Plotting script | Agent-guided. `examples/plot_two_groups.py` is the pattern |
| Accessibility report | Not implemented as a file. The palette is Okabe–Ito (**implemented**). The written check is agent-guided |

The audit should be readable as: which renderer, which test, which inputs were dropped, and which numbers were computed rather than supplied. It does not know your experimental unit unless the agent writes that into the caption or a note you keep.

## 16. Iterative review workflow

**Recommended workflow:**

1. Restate the scientific question.
2. Restate the experimental unit and what one row is.
3. Map columns onto a renderer schema in [DATA_SCHEMAS.md](DATA_SCHEMAS.md).
4. List anything the code cannot do.
5. Propose panels (mode single, auto, or specified).
6. Make previews only after you accept the proposal.
7. Record which candidate you chose and why.
8. Write final files under `figures/final/`.
9. Read `audit.json` and check labels, legend, and colour.
10. Keep the CSV, the YAML request, and the script.

## 17. Troubleshooting

Short diagnoses are below. More are in [../.cursor/skills/bioinformatics-visualization/troubleshooting.md](../.cursor/skills/bioinformatics-visualization/troubleshooting.md).

| Problem | Cause | Check | Action | Prompt |
| --- | --- | --- | --- | --- |
| Skill not detected | Chat started before the skill was copied, or the wrong project is open | `.cursor/skills/bioinformatics-visualization/SKILL.md` exists | New chat in that project | “Use the bioinformatics-visualization skill.” |
| Import failure | `PYTHONPATH` missing | `python -c "import bioinformatics_visual_evidence_atlas"` | `export PYTHONPATH=src` from this repo | “Import using PYTHONPATH=src.” |
| Missing columns | Renderer schema not met | `recommend(...)["missing_columns"]` | Rename or map columns | “Map estimate to value. Do not invent columns.” |
| Wrong category | Keyword router | Pass `category=` explicitly | Name the category from [question_router.md](../.cursor/skills/bioinformatics-visualization/question_router.md) | “Category: Survival and time-to-event analysis.” |
| Wrong family | Category default | Read `plot_family` in the recommendation | Change category or renderer | “Renderer: grouped_boxes, not grouped_bars.” |
| Too many panels | Auto mode was unbounded | Count panels | Cap at 4; hard stop at 8 | “Maximum panels: 4.” |
| Bad aggregation | Summaries treated as replicates | Read `result_type` | Split the table | “Filter to raw_observation only.” |
| Mixed result types | One `value` column, many meanings | Unique `result_type` | One type per figure | “Drop rows where result_type is not AUROC.” |
| Unreadable labels | Long group names | Look at the PNG | Shorten labels or rotate | “Keep the full group names and increase the figure width.” |
| Inconsistent scales | Modalities combined | Check `unit` | Separate panels | “One panel per modality.” |
| Missing uncertainty | Renderer has no SE input | Bar chart uses SEM of the rows you passed | Pass replicates, or plot supplied intervals in a future renderer | “These rows are replicates. Show SEM. Do not invent a CI.” |
| Misleading groups | First two groups are Welch-tested even if you have more | Read `audit.json` | State that the p-value is only the first contrast | “Do not star groups 3 and 4.” |
| Inappropriate p-value | Folds or summaries were tested | Check the unit | Remove the test from the claim | “Display the metric. Do not report the Welch p-value.” |
| No output files | `render` not called, or the folder was wrong | Look for `audit.json` | Call `render` or `compose` | “Write figures/previews/demo with render.” |
| Unsupported figure | No renderer | See the renderer list in section 8 | Stop or change the request | “If there is no renderer, say so. Do not imitate the plot.” |

## 18. Current limitations and extension points

| Limitation | Class |
| --- | --- |
| UMAP, t-SNE, Cox model, mixed model, DESeq2, IC50 fit | Planned / not yet implemented |
| Paired plot that uses `subject_id` | Planned / not yet implemented. `paired_t` is code without a renderer |
| Supplied log2 fold change volcano | Planned / not yet implemented |
| Network edge weights | Ignored by the implemented renderer |
| Panel modes and three candidates | Agent-guided |
| Accessibility report file and plot script | Agent-guided |
| Microscopy, photographs, western blots, molecular structures | Do not generate them. Place a real file the user supplies |
| Atlas template grade | Not a licence to use the matching statistical test |

Change the prompt when the data already match a renderer and only the wording was vague. Restructure the table when the unit or `result_type` is wrong. Add an adapter (a small rename or filter) when the scientific columns are right but the renderer expects `value` and `group`. Add a renderer only for a new geometry. Extend `stats.py` when a new test is required. Edit the skill instructions when the agent keeps skipping a rule that is already true of the code.
