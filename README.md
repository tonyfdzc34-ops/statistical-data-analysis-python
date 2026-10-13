# Statistical Data Analysis & Visualization with Python

**An independent, reproducible data analysis portfolio project** by Antonio Carlos Fernández Castillo.

[![Python tests](https://github.com/tonyfdzc34-ops/statistical-data-analysis-python/actions/workflows/tests.yml/badge.svg)](https://github.com/tonyfdzc34-ops/statistical-data-analysis-python/actions/workflows/tests.yml)

## Project overview

This project explores the openly licensed **UCI Wine Quality** dataset, using two related datasets containing physicochemical measurements and an ordinal sensory quality score. It demonstrates data validation, exploratory statistical inference, clearly labeled charts, automated testing, and responsible interpretation of correlations. It is **independent of any unpublished research or thesis**.

**Methods:** Python, pandas, NumPy, SciPy, Matplotlib, Spearman correlations, Benjamini–Hochberg false-discovery-rate adjustment, and an exploratory percentile bootstrap of selected associations.

## Research questions

1. What is the distribution of reported quality scores within each wine type?
2. Which physicochemical measurements show monotonic associations with quality *within* wine type?
3. Do observed patterns differ between the red and white datasets?
4. What data-quality and interpretation limits should be disclosed before drawing conclusions?

## Data source and license

**Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009).** Wine Quality [Dataset]. UCI Machine Learning Repository. [DOI:10.24432/C56S3T](https://doi.org/10.24432/C56S3T). Dataset released under **Creative Commons Attribution 4.0** ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). The dataset is credited to its original authors and is not original research by the repository owner.

> Quality ratings are **ordinal**, not laboratory measurements. The data are observational; results describe associations, **not causal effects**. The red and white datasets do not necessarily constitute a representative sample of all wines.

## Run locally

Python 3.10+ recommended. In the **repository root**:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_data.py
python -m src.analysis
python -m pytest -q
```

No API keys, login credentials, or private files are required. The download step requires internet access. If it fails, manually download `winequality-red.csv` and `winequality-white.csv` from the [UCI page](https://archive.ics.uci.edu/dataset/186/wine+quality) into `data/`, preserving their semicolon-delimited format.

## Outputs

Running the analysis generates:

- `outputs/REPORT.md` — generated statistical summary and methodological cautions.
- `outputs/tables/data_quality_audit.csv` — missing values, exact duplicates, IQR-based inspection flags.
- `outputs/tables/quality_counts.csv` — quality distribution by wine type.
- `outputs/tables/quality_spearman_associations.csv` — associations and within-group BH-adjusted q-values.
- `outputs/figures/quality_score_distribution.png` — percent distribution per wine type.
- `outputs/figures/alcohol_vs_quality.png` — jittered scatter for visibility only.
- `outputs/figures/spearman_heatmap_red.png` and `spearman_heatmap_white.png` — color-specific correlation matrices.

### Interpretation checklist

- Exact duplicate rows are **reported, not automatically deleted**.
- Observations flagged by the IQR rule are **not automatically removed**.
- Correlation analyses handle missing values pairwise, where relevant.
- Hypothesis-test p-values are adjusted using the BH procedure *within each wine type*.
- Exploratory 95% percentile bootstrap intervals are calculated for alcohol-quality associations, assuming independent sampled rows.
- Results do not imply that adjusting a chemical feature will cause a change in sensory quality.
- No predictive performance, model deployment, or external validation is claimed.

See [docs/methodology.md](docs/methodology.md) for statistical choices and limitations, including how to audit whether a chart is misleading.

## Repository layout

```text
.github/workflows/tests.yml    # basic automated checks
src/analysis.py                # reproducible pipeline
scripts/download_data.py       # documented UCI data download
tests/test_analysis.py         # unit and pipeline tests (synthetic fixtures)
data/                         # downloaded original UCI CSVs (attributed)
outputs/                      # generated figures, tables, and report
requirements.txt               # Python dependencies
docs/methodology.md            # interpretation and quality checks
```

## Reproducibility note

This repository contains **analysis code and automated tests**. Actual findings should be cited only after running the pipeline against the original UCI files. All generated outputs are computed from input data; the test suite uses synthetic fixtures **only to test software behavior**, not to support substantive conclusions.

## Contact

**Antonio Carlos Fernández Castillo** — [LinkedIn](https://www.linkedin.com/in/antonio-fern%C3%A1ndez-4a943a375/) · [GitHub](https://github.com/tonyfdzc34-ops)
