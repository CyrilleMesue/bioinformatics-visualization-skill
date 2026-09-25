# Bioinformatics visualization skill

Clone this repository into a project, or copy its skill folder into a project you already have. Cursor then uses the skill when you ask for a scientific figure.

The skill recommends a plot from the scientific question and the table you supply, then writes a publication-style figure. It does not include the source papers or their figures.

## Install

```bash
git clone https://github.com/CyrilleMesue/bioinformatics-visualization-skill.git
cd bioinformatics-visualization-skill
python -m pip install -r requirements.txt
```

Dependencies are NumPy, Matplotlib, SciPy, and scikit-learn. They are listed in `requirements.txt`.

## Use the skill in any project

From the project root:

```bash
mkdir -p .cursor/skills
cp -a /path/to/bioinformatics-visualization-skill/.cursor/skills/bioinformatics-visualization .cursor/skills/
```

Keep this repository on `PYTHONPATH` when the agent runs the plotting code:

```bash
export PYTHONPATH=/path/to/bioinformatics-visualization-skill/src
```

Open a new Cursor chat in that project and ask for a figure. Name the scientific question and attach a table whose columns match the question. When a required column is missing, the skill asks for it.

Template choice uses `milestone_8/template_rankings.json` in this repository. Human grades outrank an assumed grade. A design marked Neither is not a default.

## Example prompts

- Plot normalized MTT viability for six doses with individual replicates, uncertainty, and multiple-comparison results. Columns: `dose`, `value`.
- Compare AUROC, F1, and MCC across five models and three cohorts. Columns: `value`, `group`.
- Show whether AD and control samples separate in PCA and display the variance explained. Columns: `feature`, `sample`, `value`, and `group` for colour.
- Create a publication-ready heatmap of significant miRNA–target associations. Columns: `feature`, `sample`, `value`.
- Generate a Kaplan–Meier plot with a number-at-risk table and hazard-ratio annotation. Columns: `time`, `event`, `group`.

More routing detail is in `.cursor/skills/bioinformatics-visualization/`.

## Run one example

```bash
PYTHONPATH=src python examples/plot_two_groups.py
```

The script writes `examples/output/two_groups.png`, plus SVG and PDF. The numbers are synthetic.

## What is not in this repository

Paper PDFs, published figure images, and the human rating export stay in the local atlas. This package learns from template rankings only. Do not present a generated plot as a published result. Photographs, microscopy, and blots are not generated.
