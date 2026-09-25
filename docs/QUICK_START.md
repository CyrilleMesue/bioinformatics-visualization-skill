# Quick start

Use this page to install the skill, make one figure, compare candidates, and export files. The full explanation is in [USAGE_GUIDE.md](USAGE_GUIDE.md). Column names for each analysis are in [DATA_SCHEMAS.md](DATA_SCHEMAS.md). Copy-ready prompts are in [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md).

## 1. Install and activate

```bash
git clone https://github.com/CyrilleMesue/bioinformatics-visualization-skill.git
cd bioinformatics-visualization-skill
python -m pip install -r requirements.txt
export PYTHONPATH=src
python -c "from bioinformatics_visual_evidence_atlas.visualization import recommend; print('ok')"
PYTHONPATH=src python examples/plot_two_groups.py
```

`pip install -e .` is not the documented setup. This repository has no `[build-system]` table. Use `PYTHONPATH=src`.

Copy the skill into the project where you will chat:

```bash
mkdir -p /path/to/your-project/.cursor/skills
cp -a .cursor/skills/bioinformatics-visualization /path/to/your-project/.cursor/skills/
```

Open a new Cursor chat in that project. In the first message, point at this repository’s `src` directory and at `milestone_8/template_rankings.json`.

## 2. Prepare a long table

One row is one observation. One column is one variable. Name the experimental unit.

Synthetic group-comparison rows (`data_templates/group_comparison_long.csv`):

```csv
experiment_id,sample_id,group,value,unit
SYN_EXP1,S1,Control,1.1,relative expression
SYN_EXP1,S2,Control,0.9,relative expression
SYN_EXP1,S3,Treated,1.8,relative expression
```

## 3. Submit a prompt

```text
Primary question: Does the treated group differ from control on this synthetic assay?
One row is one independent sample. Experimental unit: sample_id.
File: data_templates/group_comparison_long.csv
Columns: group, value. Order groups Control then Treated.
Panel mode: single. Do not invent a paired test.
Write SVG, PDF, and 300 dpi PNG under figures/previews/.
```

## 4. Preview

**Implemented:** `figures.render` writes PNG (300 dpi), SVG, PDF, `plotting_data.csv`, `caption.txt`, and `audit.json`.

**Agent-guided:** choosing the file path, checking that one row means what you said, and writing a short script that calls `render`.

## 5. Ask for candidates

```text
Using the same table, group order, and Welch comparison of the first two groups,
propose three agent-guided candidates: Atlas best, Evidence best, and Compact best.
Do not draw them until I pick one. State what each version omits.
```

Generating three candidates automatically is **not implemented**. The agent proposes them.

## 6. Select one

```text
Use Compact best. Record that I chose it because it answers the question in one panel.
Render final files under figures/final/.
```

## 7. Export

Expect `figures/final/<stem>.png`, `.svg`, `.pdf`, plus `plotting_data.csv`, `caption.txt`, and `audit.json`. A separate accessibility report file is **not implemented**. Ask the agent to check Okabe–Ito colours, label overlap, and missing uncertainty in the reply.

## Multi-dataset model performance

Synthetic rows belong in `data_templates/model_performance_long.csv`. One row is one metric for one model in one dataset, not one patient.

```text
Primary question: Which synthetic model has the higher external AUROC in each dataset?
File: data_templates/model_performance_long.csv
One row is one model-dataset-metric summary, not a biological replicate.
Filter result_type=external_validation_metric and metric=AUROC.
Map model+dataset to the bar chart group column. Map estimate to value.
Panel mode: single. Do not run a t test on these summaries.
These numbers are synthetic.
```

The current bar renderer can draw those summaries only after that column mapping. It will still run a Welch test on the first two groups if you pass raw `value`/`group` rows. Say so in the prompt when that test is not appropriate.
