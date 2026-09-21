#!/usr/bin/env python3
"""
Download the Olist dataset used throughout the course.

Run from the repository root:

    python data/download.py

The files land in data/raw/olist/. Running it again is safe: it skips the
download if all nine files are already there.

Source: Brazilian E-Commerce Public Dataset by Olist
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
Licence: CC BY-NC-SA 4.0
"""

import argparse
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_URL = "https://github.com/evisp/ml-course-labs/releases/download/data-v1/olist.zip"

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "raw" / "olist"

EXPECTED = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def missing_files() -> list[str]:
    return [name for name in EXPECTED if not (TARGET / name).exists()]


def download(url: str, destination: Path) -> None:
    print(f"Downloading {url}")
    with urllib.request.urlopen(url) as response, open(destination, "wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        done = 0
        while chunk := response.read(1 << 20):
            out.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  {done / total:6.1%}  of {total / 1e6:.0f} MB", end="", flush=True)
    print()


def extract(archive: Path) -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            name = Path(member.filename).name          # flatten any folders inside the zip
            if name in EXPECTED:
                with zf.open(member) as src, open(TARGET / name, "wb") as dst:
                    shutil.copyfileobj(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the Olist dataset.")
    parser.add_argument("--url", default=DEFAULT_URL, help="where to fetch the zip from")
    parser.add_argument("--force", action="store_true", help="download even if the files exist")
    args = parser.parse_args()

    if not args.force and not missing_files():
        print(f"Already here: {len(EXPECTED)} files in {TARGET.relative_to(ROOT)}")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "olist.zip"
        try:
            download(args.url, archive)
        except Exception as error:
            print(f"Download failed: {error}", file=sys.stderr)
            print("Check your connection, or ask in the course channel.", file=sys.stderr)
            return 1
        extract(archive)

    still_missing = missing_files()
    if still_missing:
        print("These files were not found in the archive:", file=sys.stderr)
        for name in still_missing:
            print(f"  {name}", file=sys.stderr)
        return 1

    print(f"Done: {len(EXPECTED)} files in {TARGET.relative_to(ROOT)}")
    for name in EXPECTED:
        size = (TARGET / name).stat().st_size / 1e6
        print(f"  {name:<42} {size:6.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
