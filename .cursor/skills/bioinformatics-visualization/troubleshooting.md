# Troubleshooting

- Missing column: the router returns `missing_columns`. Ask for that column. Do not invent it.
- Empty category or constant variable: the test returns a missing p-value and the figure has no significance mark.
- Neither preference: choose the next eligible template, or ask the user which style to use.
- Blocked image: ask for the image file. Do not draw a micrograph, blot, or structure.
- Export: `figures.render` writes PNG, SVG, and PDF beside `plotting_data.csv`, `audit.json`, and `caption.txt`.
- Rankings look stale: rerun `python -m bioinformatics_visual_evidence_atlas.visualization.build_milestone8`. That command reads the human rating export and does not modify it.
