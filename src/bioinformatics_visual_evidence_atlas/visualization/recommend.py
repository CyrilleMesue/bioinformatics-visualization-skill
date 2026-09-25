"""Question routing. Plot choice follows the question and the data, then the rating."""

from __future__ import annotations

QUESTION_ROUTES = {
    "Group or condition comparison": {
        "family": "Bar plots with uncertainty or composition",
        "renderer": "grouped_bars",
        "companions": ["box plot of the same observations"],
        "required": ["value", "group"],
        "avoid": ["a 3D bar chart", "a pie chart of means"],
    },
    "Distribution and variability": {
        "family": "Box, violin, histogram, and distribution plots",
        "renderer": "grouped_boxes",
        "companions": ["individual points beside the boxes"],
        "required": ["value", "group"],
        "avoid": ["a bar of means when the distribution is the question"],
    },
    "Differential abundance or expression": {
        "family": "Volcano and MA plots",
        "renderer": "volcano",
        "companions": ["heatmap of significant features"],
        "required": ["feature", "value", "group"],
        "avoid": ["a single bar chart of one gene when the question is genome-wide"],
    },
    "Correlation and association": {
        "family": "Scatter and correlation plots",
        "renderer": "correlation_scatter",
        "companions": ["a correlation heatmap when many features are supplied"],
        "required": ["x", "y"],
        "avoid": ["connecting unrelated samples with a line"],
    },
    "Clustering and molecular subtypes": {
        "family": "Heatmaps",
        "renderer": "expression_heatmap",
        "companions": ["an embedding of the same matrix"],
        "required": ["feature", "sample", "value"],
        "avoid": ["a pie chart of cluster labels"],
    },
    "Dimensionality reduction and sample separation": {
        "family": "PCA, UMAP, t-SNE, and other embeddings",
        "renderer": "pca_scatter",
        "subtype_hint": "pca",
        "companions": ["a bar of variance explained"],
        "required": ["feature", "sample", "value"],
        "avoid": ["interpreting t-SNE distances as biological effect sizes"],
    },
    "Classification and model performance": {
        "family": "ROC and precision-recall curves",
        "renderer": "roc_curve",
        "companions": ["a precision-recall curve", "a calibration curve"],
        "required": ["label", "score"],
        "avoid": ["accuracy alone under class imbalance"],
    },
    "Survival and time-to-event analysis": {
        "family": "Kaplan–Meier curves",
        "renderer": "kaplan_meier",
        "companions": ["a number-at-risk table"],
        "required": ["time", "event", "group"],
        "avoid": ["a bar of mean survival when observations are censored"],
    },
    "Feature importance and model interpretation": {
        "family": "Feature-importance plots",
        "renderer": "importance_bars",
        "companions": ["a performance curve for the same model"],
        "required": ["feature", "importance"],
        "avoid": ["reading importance as a causal effect"],
    },
    "Enrichment and pathway analysis": {
        "family": "Pathway and enrichment plots",
        "renderer": "enrichment_dots",
        "subtype_hint": "enrichment",
        "companions": ["a bar of the leading terms"],
        "required": ["term", "neglog10p"],
        "avoid": ["a network drawn from an arbitrary similarity cutoff"],
    },
    "Genomic alterations and mutation patterns": {
        "family": "Mutation and oncoprint visualizations",
        "renderer": "mutation_bars",
        "companions": ["a binary alteration heatmap"],
        "required": ["value", "group"],
        "avoid": ["fabricating mutation calls"],
    },
    "Network structure and molecular interactions": {
        "family": "Network plots",
        "renderer": "network",
        "companions": ["a table of the edges that were drawn"],
        "required": ["source", "target"],
        "avoid": ["a hairball with no threshold stated"],
    },
    "Experimental validation": {
        "family": "Bar plots with uncertainty or composition",
        "renderer": "grouped_bars",
        "companions": ["the individual replicate points"],
        "required": ["value", "group"],
        "avoid": ["a western-blot photograph that was not supplied"],
    },
    "Biomarker discovery and validation": {
        "family": "ROC and precision-recall curves",
        "renderer": "roc_curve",
        "companions": ["importance bars for the candidate features"],
        "required": ["label", "score"],
        "avoid": ["reporting a training AUC as external validation"],
    },
    "Temporal or dose-response patterns": {
        "family": "Dose-response and time-course plots",
        "renderer": "dose_response",
        "companions": ["individual replicates"],
        "required": ["dose", "value"],
        "avoid": ["connecting doses that were not measured"],
    },
    "Multi-omics integration": {
        "family": "Heatmaps",
        "renderer": "expression_heatmap",
        "companions": ["a PCA of the same matrix"],
        "required": ["feature", "sample", "value"],
        "avoid": ["stacking unrelated scales on one axis without stating the transform"],
    },
    "Computational cost and scalability": {
        "family": "Bar plots with uncertainty or composition",
        "renderer": "grouped_bars",
        "companions": ["a line of runtime against input size"],
        "required": ["value", "group"],
        "avoid": ["a biological heatmap of runtime numbers"],
    },
    "Data quality and measurement reliability": {
        "family": "Box, violin, histogram, and distribution plots",
        "renderer": "grouped_boxes",
        "companions": ["a missingness bar"],
        "required": ["value", "group"],
        "avoid": ["hiding missing samples"],
    },
    "Spatial or single-cell organization": {
        "family": "PCA, UMAP, t-SNE, and other embeddings",
        "renderer": "pca_scatter",
        "subtype_hint": "pca",
        "companions": ["a user-supplied microscopy image in a separate panel"],
        "required": ["feature", "sample", "value"],
        "avoid": ["a generated microscopy image"],
    },
    "Workflow, architecture, or methodological explanation": {
        "family": "Workflow and architecture diagrams",
        "renderer": "workflow_steps",
        "companions": [],
        "required": ["step"],
        "avoid": ["presenting a schematic as a measured result"],
    },
}

KEYWORD_CATEGORY = [
    ("kaplan", "Survival and time-to-event analysis"),
    ("survival", "Survival and time-to-event analysis"),
    ("hazard", "Survival and time-to-event analysis"),
    ("auroc", "Classification and model performance"),
    ("roc", "Classification and model performance"),
    ("classification", "Classification and model performance"),
    ("dose", "Temporal or dose-response patterns"),
    ("mtt", "Temporal or dose-response patterns"),
    ("viability", "Temporal or dose-response patterns"),
    ("qpcr", "Group or condition comparison"),
    ("mirna", "Correlation and association"),
    ("heatmap", "Clustering and molecular subtypes"),
    ("pca", "Dimensionality reduction and sample separation"),
    ("enrichment", "Enrichment and pathway analysis"),
    ("pathway", "Enrichment and pathway analysis"),
    ("network", "Network structure and molecular interactions"),
    ("importance", "Feature importance and model interpretation"),
    ("volcano", "Differential abundance or expression"),
    ("differential", "Differential abundance or expression"),
    ("correlation", "Correlation and association"),
    ("paired", "Group or condition comparison"),
]


def infer_category(question: str, category: str | None) -> str:
    if category in QUESTION_ROUTES:
        return category
    text = question.lower()
    for keyword, name in KEYWORD_CATEGORY:
        if keyword in text:
            return name
    return "Group or condition comparison"


def recommend(question: str, columns: list[str], category: str | None = None, rankings: list[dict] | None = None) -> dict:
    chosen = route(question, columns, category)
    if rankings and not chosen["missing_columns"]:
        matches = [
            row for row in rankings
            if row["plot_family"] == chosen["plot_family"] and row["default_eligible"] == "yes"
        ]
        hint = chosen.get("subtype_hint", "")
        hinted = [row for row in matches if hint and hint in row["plot_subtype"]]
        if hinted:
            matches = hinted
        if matches:
            best = sorted(matches, key=lambda row: (row["rank"], -(row["mean_emphasized_weight"] or 0)))[0]
            chosen["template_id"] = best["template_id"]
            chosen["emphasized_weight"] = best["mean_emphasized_weight"]
            chosen["preferred_version"] = best["preferred_version_mode"]
            chosen["rank"] = best["rank"]
            chosen["provisional"] = best["provisional"]
    chosen.setdefault("template_id", "")
    chosen.setdefault("emphasized_weight", None)
    chosen.setdefault("preferred_version", "")
    chosen.setdefault("provisional", "no")
    return chosen


def route(question: str, columns: list[str], category: str | None = None) -> dict:
    chosen = infer_category(question, category)
    spec = QUESTION_ROUTES[chosen]
    missing = [name for name in spec["required"] if name not in columns]
    return {
        "question_category": chosen,
        "plot_family": spec["family"],
        "renderer": spec["renderer"],
        "subtype_hint": spec.get("subtype_hint", ""),
        "companions": spec["companions"],
        "missing_columns": missing,
        "avoid": spec["avoid"],
        "rationale": (
            f"The question is routed to {chosen}. The primary display is {spec['family']} "
            f"because that encoding answers the comparison the question asks for."
        ),
    }
