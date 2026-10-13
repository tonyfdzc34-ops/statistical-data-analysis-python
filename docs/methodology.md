# Methods, limitations, and chart-review checklist

## Scientific question

What patterns in physical and chemical measurements accompany recorded quality scores in the UCI Wine Quality datasets? These are **exploratory** relationships, not proof of causation.

## Analysis decisions

1. Read the original semicolon-delimited source files and label each observation with its dataset (`red`/`white`).
2. Validate column names, numeric types and plausible quality-score range. Stop on schema errors rather than silently recoding unexpected columns.
3. Audit missingness, exact duplicate profiles and IQR-based flags. **Preserve** data; duplicates may arise from separate wines with identical recorded characteristics.
4. Report frequencies of ordinal quality scores as **within-type percentages**, not misleading pooled counts.
5. Calculate rank-based Spearman correlations by wine type. Rank association is suited to ordinal quality ratings, but does not correct sampling bias or confounding.
6. Apply Benjamini–Hochberg false discovery rate adjustment within each set of 11 feature-quality tests. These q-values remain exploratory.
7. Calculate a nonparametric percentile bootstrap interval for the alcohol-quality Spearman correlation within each type. Resampling assumes independent observations, which the available metadata cannot verify.
8. Output separate, labeled figures and tables. Plot jitter on quality is **visualization-only**.

## What a reviewer should check

- Does every axis have a label, units where meaningful, and an explicit scale?
- Are counts or percentages normalized by the proper denominator?
- Are red and white records combined in ways that conceal subgroup differences?
- Is an ordinal score being treated as if it is a precise physical measurement?
- Are apparent outliers automatically removed without an external rationale?
- Are exact duplicate profiles incorrectly asserted to be duplicate sampled wines?
- Are p-values interpreted without considering multiple comparisons?
- Does the interpretation claim causation from observational data?
- Do bootstrapped uncertainty intervals rely on unrealistic independence assumptions?

## Suggested next iteration

A subsequent version could add cross-validation with appropriately justified baselines and uncertainty, alongside a held-out test set and feature-leakage audit. This version deliberately focuses on statistically defensible interpretation and chart quality, the primary intended portfolio skill.
