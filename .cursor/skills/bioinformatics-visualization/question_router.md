# Scientific-question router

Each category lists the primary plot, companions, required columns, and a plot to avoid.

| Category | Primary | Companions | Required columns | Avoid |
| --- | --- | --- | --- | --- |
| Group or condition comparison | Grouped bars with uncertainty | Boxes of the same observations | value, group | 3D bars |
| Distribution and variability | Boxes | Individual points | value, group | Bar of means when the distribution is the question |
| Differential abundance or expression | Volcano | Heatmap of significant features | feature, value, group | One gene bar for a genome-wide question |
| Correlation and association | Scatter with correlation | Heatmap when many features are supplied | x, y | Lines between unrelated samples |
| Clustering and molecular subtypes | Heatmap | Embedding of the same matrix | feature, sample, value | Pie of cluster labels |
| Dimensionality reduction and sample separation | PCA | Variance-explained annotation | feature, sample, value | Reading t-SNE distance as an effect size |
| Classification and model performance | ROC | Precision-recall and calibration | label, score | Accuracy alone under imbalance |
| Survival and time-to-event analysis | Kaplan–Meier | Number at risk | time, event, group | Mean survival when times are censored |
| Feature importance and model interpretation | Horizontal bars | Performance curve | feature, importance | Reading importance as causation |
| Enrichment and pathway analysis | Enrichment dots | Bars of leading terms | term, neglog10p | Untresholded hairball |
| Genomic alterations and mutation patterns | Alteration bars | Binary alteration heatmap | sample, value | Fabricated mutation calls |
| Network structure and molecular interactions | Network of supplied edges | Edge table | source, target | Edges that were not supplied |
| Experimental validation | Bars with replicates | User-supplied assay image | value, group | Generated blot or micrograph |
| Biomarker discovery and validation | ROC | Importance bars | label, score | Training AUC reported as external validation |
| Temporal or dose-response patterns | Dose or time curve | Replicate points | dose, value | Connecting unmeasured doses |
| Multi-omics integration | Heatmap | PCA of the same matrix | feature, sample, value | Unstated mixed scales |
| Computational cost and scalability | Bars or a runtime line | — | value, group | Biological heatmap of runtime |
| Data quality and measurement reliability | Boxes | Missingness note | value, group | Hidden missing samples |
| Spatial or single-cell organization | Embedding | User-supplied image panel | feature, sample, value | Generated microscopy |
| Workflow, architecture, or methodological explanation | Text schematic | — | step | A schematic presented as a measurement |

Compatible designs are independent, paired, repeated, nested, censored, spatial, temporal, or networked, matching the columns. Paired data need a subject identifier. Censored data need time and event. Rankings in `milestone_8/template_rankings.json` supply the highest-weight template and the fallback inside the same family.
