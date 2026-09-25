# Statistical safeguards

Compute statistics from the supplied table. If a number cannot be computed, omit it.

- Independent groups: Welch t test. Paired observations: paired t test. Do not switch these.
- Repeated measurements need a subject identifier. Do not treat repeats as independent.
- Multiple features: Benjamini–Hochberg on the computed p-values.
- Report sample size, and a confidence interval or SEM only when it is computed.
- Drop missing values and state how many were dropped.
- Class imbalance: show ROC or precision-recall, not accuracy alone.
- Cross-validation scores stay at the fold or model grain supplied by the user.
- Survival uses the Kaplan–Meier estimator, a two-group log-rank test, and a Mantel–Haenszel hazard ratio. Censoring is the event column.
- State batch or cohort when it is a column. Do not adjust for a batch that was not supplied.
- Logarithmic axes require positive values. State the transform.
- Networks draw only supplied edges. State the threshold the user used.
- PCA reports variance explained from the singular values. Do not claim UMAP unless that embedding was computed.
- Mark synthetic demonstrations in the caption.

Separate the statistical result from a biological interpretation.
