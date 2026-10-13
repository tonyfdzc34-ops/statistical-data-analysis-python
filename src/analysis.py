"""Reproducible Wine Quality data audit, statistical exploration and plots.

Run: python -m src.analysis --data data --out outputs

All analyses are descriptive or exploratory. Sensory quality is ordinal, and
observed relationships must not be interpreted as causal effects.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

FEATURES = [
    "fixed acidity", "volatile acidity", "citric acid", "residual sugar",
    "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density",
    "pH", "sulphates", "alcohol",
]
COLORS = ("red", "white")


def read_datasets(data_dir: Path) -> pd.DataFrame:
    """Read both semicolon-delimited UCI files and preserve observations."""
    groups = []
    for color in COLORS:
        path = data_dir / f"winequality-{color}.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run 'python scripts/download_data.py' first."
            )
        df = pd.read_csv(path, sep=";")
        expected = set(FEATURES + ["quality"])
        if set(df.columns) != expected:
            raise ValueError(
                f"Column mismatch in {path}: missing={expected - set(df.columns)}; "
                f"unexpected={set(df.columns) - expected}"
            )
        for col in FEATURES + ["quality"]:
            df[col] = pd.to_numeric(df[col], errors="raise")
        if df["quality"].notna().any() and not np.allclose(
            df["quality"].dropna(), df["quality"].dropna().round()
        ):
            raise ValueError(f"Quality must be recorded as an integer score in {path}")
        if not df["quality"].dropna().between(0, 10).all():
            raise ValueError(f"Quality outside expected 0–10 scale in {path}")
        df.insert(0, "wine_type", color)
        groups.append(df)
    return pd.concat(groups, axis=0, ignore_index=True)


def audit(df: pd.DataFrame) -> pd.DataFrame:
    """Report potential data issues without altering source observations."""
    rows = []
    for group, subset in df.groupby("wine_type", sort=True):
        outlier_flags = pd.DataFrame(index=subset.index)
        for feature in FEATURES:
            x = subset[feature].dropna()
            q1, q3 = x.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                outlier_flags[feature] = subset[feature].lt(q1 - 1.5 * iqr) | subset[feature].gt(q3 + 1.5 * iqr)
            else:
                outlier_flags[feature] = False
        rows.append({
            "wine_type": group,
            "rows": len(subset),
            "missing_cells": int(subset.isna().sum().sum()),
            "rows_with_missing_values": int(subset.isna().any(axis=1).sum()),
            "exact_duplicate_rows": int(subset.duplicated(subset=FEATURES + ["quality"]).sum()),
            "rows_with_iqr_feature_flags": int(outlier_flags.any(axis=1).sum()),
            "quality_min": subset["quality"].min(),
            "quality_median": subset["quality"].median(),
            "quality_max": subset["quality"].max(),
        })
    return pd.DataFrame(rows)


def benjamini_hochberg(p: np.ndarray) -> np.ndarray:
    """BH FDR adjustment of valid p-values, retaining NaN positions."""
    p = np.asarray(p, dtype=float)
    result = np.full_like(p, np.nan)
    valid = np.flatnonzero(np.isfinite(p))
    if not len(valid):
        return result
    order = valid[np.argsort(p[valid])]
    n = len(valid)
    adj = np.minimum.accumulate((p[order] * n / np.arange(1, n + 1))[::-1])[::-1]
    result[order] = np.clip(adj, 0, 1)
    return result


def spearman_table(df: pd.DataFrame) -> pd.DataFrame:
    """Associations WITHIN wine type; BH adjustment within each group."""
    records = []
    for color, frame in df.groupby("wine_type", sort=True):
        subset_rows = []
        for feature in FEATURES:
            valid = frame[[feature, "quality"]].dropna()
            if len(valid) < 4 or valid[feature].nunique() < 2 or valid["quality"].nunique() < 2:
                rho, p = float("nan"), float("nan")
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    rho, p = spearmanr(valid[feature], valid["quality"])
            subset_rows.append({"wine_type": color, "feature": feature,
                                "n_complete": len(valid), "spearman_rho": rho, "p_value": p})
        adjusted = benjamini_hochberg(np.array([r["p_value"] for r in subset_rows]))
        for r, q in zip(subset_rows, adjusted):
            r["fdr_bh_q_value"] = q
        records.extend(subset_rows)
    return pd.DataFrame(records)


def bootstrap_spearman(x: pd.Series, y: pd.Series, repeats: int = 500,
                       seed: int = 2026) -> tuple[float, float]:
    """Illustrative percentile bootstrap interval; assumes independent rows."""
    paired = pd.concat([x, y], axis=1).dropna().to_numpy(dtype=float)
    if len(paired) < 10:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repeats):
        draw = paired[rng.integers(len(paired), size=len(paired))]
        if len(np.unique(draw[:, 0])) >= 2 and len(np.unique(draw[:, 1])) >= 2:
            values.append(float(spearmanr(draw[:, 0], draw[:, 1]).statistic))
    if len(values) < 10:
        return (float("nan"), float("nan"))
    lo, hi = np.quantile(values, [0.025, 0.975])
    return (float(lo), float(hi))


def save_quality_plot(df: pd.DataFrame, directory: Path) -> None:
    freq = df.groupby(["quality", "wine_type"]).size().unstack(fill_value=0)
    pct = freq.div(freq.sum(axis=0), axis=1).mul(100)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    scores = pct.index.to_numpy(dtype=float)
    for offset, color, shade in [(-0.19, "red", "#c14953"), (0.19, "white", "#267fa3")]:
        ax.bar(scores + offset, pct[color], width=0.36, color=shade, label=color.title())
    ax.set(xlabel="Recorded quality score (ordinal)", ylabel="Within-type share of observations (%)",
           title="Distribution of recorded quality scores")
    ax.set_xticks(scores)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(directory / "quality_score_distribution.png", dpi=170)
    plt.close(fig)


def save_alcohol_plot(df: pd.DataFrame, directory: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    rng = np.random.default_rng(2026)
    for color, shade in [("red", "#c14953"), ("white", "#267fa3")]:
        f = df.loc[df["wine_type"] == color, ["alcohol", "quality"]].dropna()
        j = rng.uniform(-0.15, 0.15, len(f))  # only visualization jitter, not model input
        ax.scatter(f["alcohol"], f["quality"] + j, s=11, alpha=0.26,
                   color=shade, label=f"{color.title()} (n={len(f):,})", rasterized=True)
    ax.set(xlabel="Alcohol (% by volume)", ylabel="Recorded quality score (jittered for visibility)",
           title="Alcohol content and recorded quality — observational data")
    ax.legend(frameon=False)
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(directory / "alcohol_vs_quality.png", dpi=170)
    plt.close(fig)


def save_correlations(df: pd.DataFrame, directory: Path) -> None:
    for color in COLORS:
        group = df[df["wine_type"] == color]
        correlation = group[FEATURES + ["quality"]].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(correlation, vmin=-1, vmax=1, cmap="coolwarm")
        names = [a.replace(" ", "\n") if len(a)>15 else a for a in correlation.columns]
        ax.set_xticks(range(len(names)), names, rotation=75, ha="right", fontsize=8)
        ax.set_yticks(range(len(names)), names, fontsize=8)
        ax.set_title(f"Spearman rank correlations — {color} wine")
        fig.colorbar(im, ax=ax, label="Spearman rho", shrink=0.77)
        fig.tight_layout()
        fig.savefig(directory / f"spearman_heatmap_{color}.png", dpi=170)
        plt.close(fig)


def save_report(df: pd.DataFrame, associations: pd.DataFrame, directory: Path) -> None:
    lines = [
        "# Exploratory results — UCI Wine Quality",
        "",
        "*Generated by `python -m src.analysis`. Descriptive/exploratory results only.*",
        "",
        f"Total records: **{len(df):,}**. Types: **{', '.join(COLORS)}**.",
        "",
        "## Interpreting the outputs",
        "",
        "- Quality is an **ordinal sensory rating**; it is not a continuous laboratory measurement.",
        "- Correlations are calculated **within** wine type to reduce a common source of confounding.",
        "- Feature p-values are adjusted separately within each wine type using Benjamini–Hochberg FDR.",
        "- Identical rows are **flagged, not dropped**: they may be distinct wines with the same measured values.",
        "- IQR outlier flags indicate values to inspect, **not** automatic measurement errors.",
        "- Associations do not establish causes; convenience/selection bias and unrecorded factors remain possible.",
        "- Percentile bootstrap assumes independent samples, which may not be verifiable from released metadata.",
        "",
        "## Alcohol vs quality — within-type Spearman associations",
        "",
        "| Type | n | Spearman rho | BH q-value | 95% bootstrap percentile interval |",
        "|---|---:|---:|---:|---|",
    ]
    for color in COLORS:
        r = associations[(associations.wine_type == color) & (associations.feature == "alcohol")].iloc[0]
        sub = df[df.wine_type == color]
        lo, hi = bootstrap_spearman(sub.alcohol, sub.quality)
        lines.append(f"| {color.title()} | {int(r.n_complete):,} | {r.spearman_rho:.3f} | "
                     f"{r.fdr_bh_q_value:.3g} | [{lo:.3f}, {hi:.3f}] |")
    lines += ["", "Other correlations and audit flags are in `outputs/tables/`.", "",
              "## Figures", "",
              "![Quality distribution](figures/quality_score_distribution.png)", "",
              "![Alcohol and quality](figures/alcohol_vs_quality.png)", "",
              "![Correlations: red](figures/spearman_heatmap_red.png)", "",
              "![Correlations: white](figures/spearman_heatmap_white.png)", "",
              "## Attribution", "",
              "Cortez et al. (2009), [UCI Wine Quality](https://doi.org/10.24432/C56S3T), CC BY 4.0.", ""]
    (directory / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(data_dir: Path, output_dir: Path) -> None:
    df = read_datasets(data_dir)
    figures, tables = output_dir / "figures", output_dir / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    audit(df).to_csv(tables / "data_quality_audit.csv", index=False)
    correlations = spearman_table(df)
    correlations.to_csv(tables / "quality_spearman_associations.csv", index=False, float_format="%.7g")
    df.groupby(["wine_type", "quality"]).size().rename("n").reset_index().to_csv(
        tables / "quality_counts.csv", index=False
    )
    save_quality_plot(df, figures)
    save_alcohol_plot(df, figures)
    save_correlations(df, figures)
    save_report(df, correlations, output_dir)
    print(f"Processed {len(df):,} records. See {output_dir / 'REPORT.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the UCI Wine Quality portfolio analysis")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    run(args.data, args.out)
