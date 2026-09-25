# Documentation audit

Milestone 9/9. Documentation only. Plotting code, atlas rankings, and human ratings were not changed.

## Files created

- `docs/USAGE_GUIDE.md`
- `docs/QUICK_START.md`
- `docs/DATA_SCHEMAS.md`
- `docs/PROMPT_LIBRARY.md`
- `docs/DOCUMENTATION_AUDIT.md`
- `figure_requests/figure_request_template.yaml`
- `figure_requests/examples/simple_group_comparison.yaml`
- `figure_requests/examples/multi_dataset_model_performance.yaml`
- `figure_requests/examples/paired_qpcr.yaml`
- `figure_requests/examples/dose_response.yaml`
- `figure_requests/examples/survival.yaml`
- `data_templates/data_dictionary_template.csv`
- `data_templates/group_comparison_long.csv`
- `data_templates/repeated_measure_long.csv`
- `data_templates/model_performance_long.csv`
- `data_templates/differential_results_long.csv`
- `data_templates/survival_long.csv`
- `data_templates/enrichment_long.csv`
- `data_templates/network_edges.csv`

## Files modified

- `README.md`
- `.cursor/skills/bioinformatics-visualization/SKILL.md`
- `.cursor/skills/bioinformatics-visualization/examples.md`
- `.cursor/skills/bioinformatics-visualization/question_router.md`
- `.cursor/skills/bioinformatics-visualization/plot_families.md`
- `.cursor/skills/bioinformatics-visualization/safeguards.md`
- `.cursor/skills/bioinformatics-visualization/troubleshooting.md`

## Validation performed

- Every new path listed above exists.
- Markdown links in `README.md`, `docs/*.md`, and the skill directory were resolved relative to the file that contains them. Broken links found: 0.
- YAML under `figure_requests/` parsed with `yaml.safe_load`.
- Every CSV under `data_templates/` has the same field count on every row.
- Renderer names in the guides match `RENDERERS` in `visualization/figures.py` (18 names).
- `PYTHONPATH=src` import of `recommend` and `RENDERERS` succeeded.
- `PYTHONPATH=src python examples/plot_two_groups.py` wrote `examples/output/two_groups.png`.
- `milestone_8/template_rankings.json` was not modified (`git status` did not list it).

## Broken links

None found.

## Capabilities verified against code

| Claim in the guides | Code |
| --- | --- |
| `recommend` returns category, renderer, missing columns, template id | `visualization/recommend.py` |
| `render` writes PNG at 300 dpi, SVG, PDF, plotting CSV, caption, audit | `figures.render`, `style.save_figure` |
| `compose` writes caption and audit, letters A–H, and does not write the plotting CSV | `figures.compose` |
| Bar charts use Welch on the first two groups | `figures._bars` |
| `paired_t` is unused by renderers | `stats.paired_t` has no caller in `figures.py` |
| Volcano recomputes Welch and Benjamini–Hochberg | `figures._volcano` |
| PCA fills blanks with 0 and does not scale | `figures._pca` |
| Kaplan–Meier hazard ratio is Mantel–Haenszel | `stats.hazard_ratio` |
| Mutation bars require `value` and `group` | `figures._mutation` calls `_bars` |
| Panel modes and three candidates are not function arguments | No such parameters on `render` or `recommend` |

## Limitations identified

- No editable install metadata (`[build-system]` is absent).
- No paired renderer, no Cox model, no UMAP, no DESeq2 input path.
- No accessibility report file.
- `compose` stops at eight panels.

## Unresolved documentation uncertainties

- GitHub link checks were local path checks, not a browse of the rendered GitHub pages.
- `pip install -e .` was not run, because the project file does not declare a build system.

## Commands

```bash
python3 -c "import yaml,csv,re,pathlib"  # link, YAML, and CSV checks
PYTHONPATH=src python -c "from bioinformatics_visual_evidence_atlas.visualization.figures import RENDERERS"
PYTHONPATH=src python examples/plot_two_groups.py
```

## Status

Pass. Code behaviour was not changed.
