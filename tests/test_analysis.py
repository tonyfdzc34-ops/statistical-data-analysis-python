from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from scripts.download_data import collect_csv_from_zip
from src.analysis import FEATURES, audit, benjamini_hochberg, read_datasets, run, spearman_table


def _fixture_dataset(n=40, seed=19):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({feature: rng.uniform(0.1, 4, n) for feature in FEATURES})
    df["alcohol"] = rng.uniform(8, 14, n)
    df["quality"] = np.clip(np.round(3 + 0.25 * df["alcohol"] + rng.normal(0, 0.7, n)), 0, 10).astype(int)
    return df


def test_bh_adjustment_preserves_order_and_nan():
    got = benjamini_hochberg(np.array([0.04, 0.01, np.nan, 0.03]))
    assert got[0] == pytest.approx(0.04)
    assert got[1] == pytest.approx(0.03)
    assert np.isnan(got[2])
    assert got[3] == pytest.approx(0.04)


def test_read_preserves_duplicates_and_color(tmp_path):
    for name in ("red", "white"):
        df = _fixture_dataset(35)
        df.iloc[1] = df.iloc[0]  # legitimate possibility: repeated measurement profile
        df.to_csv(tmp_path / f"winequality-{name}.csv", sep=";", index=False)
    got = read_datasets(tmp_path)
    checks = audit(got)
    assert len(got) == 70
    assert set(got.wine_type) == {"red", "white"}
    assert (checks.exact_duplicate_rows == 1).all()
    assert len(spearman_table(got)) == 22


def test_missing_file_raises_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="download_data"):
        read_datasets(tmp_path)


def test_schema_and_quality_validation(tmp_path):
    for name in ("red", "white"):
        df = _fixture_dataset(35)
        if name == "red":
            df["quality"] = 14
        df.to_csv(tmp_path / f"winequality-{name}.csv", sep=";", index=False)
    with pytest.raises(ValueError, match="0–10"):
        read_datasets(tmp_path)


def test_full_pipeline_with_synthetic_test_fixture(tmp_path):
    raw = tmp_path / "data"
    raw.mkdir()
    for i, name in enumerate(("red", "white")):
        _fixture_dataset(n=38, seed=14 + i).to_csv(raw / f"winequality-{name}.csv", sep=";", index=False)
    output = tmp_path / "outputs"
    run(raw, output)
    assert (output / "REPORT.md").exists()
    assert len(list((output / "figures").glob("*.png"))) == 4
    assert len(list((output / "tables").glob("*.csv"))) == 3


def test_nested_zip_extraction():
    nested = BytesIO()
    with ZipFile(nested, "w") as inner:
        inner.writestr("winequality-red.csv", b'"fixed acidity";"quality"\n7;5\n')
    top = BytesIO()
    with ZipFile(top, "w") as outer:
        outer.writestr("winequality.zip", nested.getvalue())
    found = collect_csv_from_zip(top.getvalue())
    assert found["winequality-red.csv"].startswith(b'"fixed acidity"')
