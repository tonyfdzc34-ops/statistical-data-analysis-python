"""Download the openly licensed UCI Wine Quality source dataset.

Usage: python scripts/download_data.py
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile
import argparse

UCI_URL = "https://archive.ics.uci.edu/static/public/186/wine+quality.zip"
NAMES = {"winequality-red.csv", "winequality-white.csv"}


def collect_csv_from_zip(blob: bytes, depth: int = 0) -> dict[str, bytes]:
    """Support either flat or nested ZIP archives returned by UCI."""
    if depth > 3:
        raise ValueError("ZIP archive nesting depth exceeded")
    with ZipFile(BytesIO(blob)) as zf:
        found = {}
        for name in zf.namelist():
            base = Path(name).name.lower()
            if base in NAMES:
                found[base] = zf.read(name)
            elif base.endswith(".zip"):
                found.update(collect_csv_from_zip(zf.read(name), depth + 1))
        return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    request = Request(UCI_URL, headers={"User-Agent": "Mozilla/5.0 (research portfolio)"})
    try:
        with urlopen(request, timeout=45) as res:
            files = collect_csv_from_zip(res.read())
    except (OSError, BadZipFile) as exc:
        raise SystemExit(
            "Automated download failed. Download 'winequality-red.csv' and "
            "'winequality-white.csv' manually from the UCI dataset page "
            "(https://archive.ics.uci.edu/dataset/186/wine+quality), "
            f"then place both files in {args.output}/. Details: {exc}"
        ) from exc
    if set(files) != NAMES:
        raise SystemExit(f"Unexpected archive: found {list(files)}, expected {sorted(NAMES)}")
    for name, content in sorted(files.items()):
        if not content.lstrip().startswith(b'"fixed acidity"'):
            raise SystemExit(f"Unexpected CSV header in {name}; stopping for manual inspection")
        path = args.output / name
        path.write_bytes(content)
        print(f"Saved {path} ({len(content):,} bytes)")
    print("Source: Cortez et al. (2009), UCI Wine Quality, CC BY 4.0")


if __name__ == "__main__":
    main()
