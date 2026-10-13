# Statistical Findings and Validation — UCI Wine Quality Dataset

**Portfolio analysis | Python | Exploratory Data Analysis | Statistical Validation**

## Scope and provenance

This analysis uses the publicly available UCI Wine Quality datasets (red and white Vinho Verde wines), associated with Cortez et al. (2009). The records include eleven physicochemical measurements and an ordinal recorded quality score. The two wine types were examined separately for association analyses. The original data are distributed under a CC BY 4.0 license; the dataset source and attribution should be preserved in the project README.

## Dataset audit

| Audit measure | Red wine | White wine |
|---|---:|---:|
| Observations | 1,599 | 4,898 |
| Missing cells | 0 | 0 |
| Exact duplicate rows | 240 (15.0%) | 937 (19.1%) |
| Rows flagged by feature-wise IQR criteria | 405 (25.3%) | 883 (18.0%) |
| Recorded quality-score range | 3–8 | 3–9 |
| Median quality score | 6 | 6 |

The files contain **6,497 observations** in total. Exact repeated rows were identified, but they should **not automatically be treated as erroneous duplicates**: there is no unique observation identifier available to establish whether identical records represent repeated measurements or different observations with matching values. Similarly, IQR flags identify observations requiring attention, not necessarily incorrect data. Removal or modification would require a stated, justified rule and sensitivity analysis.

## Quality-score distributions

- The modal recorded score among red wines is **5**, accounting for **681/1,599 = 42.6%** of red-wine records.
- The modal recorded score among white wines is **6**, accounting for **2,198/4,898 = 44.9%** of white-wine records.
- Relative frequencies were computed within wine type so distributions remain comparable despite unequal sample sizes.

## Spearman associations with recorded quality

Spearman rank correlation was used because the outcome is ordinal. The table below reports selected effect sizes from the generated association file; signs and magnitudes are descriptive, and **correlations do not establish causality**.

| Physicochemical characteristic | Red wine Spearman ρ | White wine Spearman ρ |
|---|---:|---:|
| Alcohol content | +0.479 | +0.440 |
| Volatile acidity | −0.381 | −0.197 |
| Density | −0.177 | −0.348 |
| Chlorides | −0.190 | −0.314 |
| Sulphates | +0.377 | +0.033 |

The largest positive association with recorded quality in either group is alcohol content. For red wines, volatile acidity and sulphates have additional associations of moderate descriptive magnitude. For white wines, density and chlorides have notable negative associations.

Benjamini–Hochberg false discovery rate (FDR) correction was applied **separately within each wine type**, over eleven feature–quality tests. The tabulated adjusted q-values are numerically consistent with this procedure. **Nine of eleven** feature–quality associations have adjusted q-values below 0.05 for red wine, and **nine of eleven** for white wine. Statistical significance should not be confused with practical importance: for example, the positive association between sulphates and quality for white wine (ρ = +0.033) is very small despite an FDR-adjusted q-value below 0.05.

## Visualization gallery

The figures below are generated reproducibly by `python -m src.analysis` and should appear after the `outputs/` directory has been uploaded.

![Quality-score distribution](../outputs/figures/quality_score_distribution.png)

![Alcohol and quality](../outputs/figures/alcohol_vs_quality.png)

![Red wine Spearman heatmap](../outputs/figures/spearman_heatmap_red.png)

![White wine Spearman heatmap](../outputs/figures/spearman_heatmap_white.png)

## Visualization review

1. **Recorded score distribution:** Uses within-group percentages to account for different group sizes; labels correctly identify the ordinal score scale.
2. **Red-wine Spearman heatmap:** Consistent with the reported association magnitudes, with a symmetric matrix, unit diagonal, and color scale from −1 to +1.
3. **White-wine Spearman heatmap:** Highlights correlations among physicochemical characteristics as well as their separate association with quality.
4. **Alcohol versus quality scatter:** Uses vertical jitter to reduce overlap at discrete score values; jitter serves visualization only and should never be interpreted as changes in measured quality.

## Limitations and interpretation

- Results are exploratory and observational. Neither statistical significance nor the direction of association implies causation.
- Group comparisons are descriptive; this analysis does not adjust for all possible confounders or quantify uncertainty in between-group differences.
- Large sample sizes can yield small p-values for relationships with minimal effect sizes. Report correlation coefficients and uncertainty rather than p-values alone.
- Without unique sample IDs, exact repeated rows cannot be definitively classified as data-entry errors.
- Exploratory IQR flags are not deletion criteria; retain the original observations unless further justification is available.
- The outcome is an ordinal quality rating rather than a continuous physical measurement.

## Reproducibility status

The user executed `python -m src.analysis` successfully and reported that **6,497 records** were processed, and ran `python -m pytest -q` with **6 tests passing**. These automated checks do not establish that all methodological choices are optimal. This findings note was reviewed against the supplied figures and three generated CSV tables. The automatically generated `outputs/REPORT.md` has now been reviewed against the supplied CSV tables and four figures. The reported group sizes, alcohol–quality Spearman coefficients, and BH-adjusted q-values agree to the displayed precision. This is a consistency review, not an independent replication of the entire analysis pipeline or proof that all modeling choices are optimal.

## Source tables and generated report

- [Automated exploratory report](../outputs/REPORT.md)
- [Data quality audit](../outputs/tables/data_quality_audit.csv)
- [Quality-score counts](../outputs/tables/quality_counts.csv)
- [Feature–quality Spearman associations](../outputs/tables/quality_spearman_associations.csv)

The Spearman significance statements reflect within-wine-type Benjamini–Hochberg adjustments across 11 features. Statistical significance is distinct from practical relevance. Percentile bootstrap intervals in the automated report rely on an independence assumption that cannot be fully validated from the released data metadata.

## Dataset reference

Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. *Decision Support Systems*, 47(4), 547–553. Dataset: [UCI Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality).
