#!/usr/bin/env python3
"""
Download the datasets used in the course.

Run from the repository root:

    python data/download.py            # Olist, used in the Block 1 labs
    python data/download.py --taxi     # New York taxi trips, used in Project 1

Files land in data/raw/olist/ or data/raw/taxi/. Running it again is safe:
nothing is downloaded if the files are already there.

Sources and licences:
    Olist: Brazilian E-Commerce Public Dataset by Olist, CC BY-NC-SA 4.0
           https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
    Taxi:  NYC Taxi and Limousine Commission trip records, NYC Open Data
           https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
"""

import argparse
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

RELEASES = "https://github.com/evisp/ml-course-labs/releases/download"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

OLIST_FILES = [
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

TAXI_FILES = [
    "yellow_tripdata_2026_sample.parquet",
    "taxi_zone_lookup.csv",
    "taxi_zones.zip",
    "data_dictionary_trip_records_yellow.pdf",
]


def fetch(url: str, destination: Path) -> None:
    print(f"Downloading {url.rsplit('/', 1)[-1]}")
    with urllib.request.urlopen(url) as response, open(destination, "wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        done = 0
        while chunk := response.read(1 << 20):
            out.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  {done / total:6.1%}  of {total / 1e6:.0f} MB", end="", flush=True)
    print()


def get_olist(base: str, force: bool) -> list[Path]:
    target = RAW / "olist"
    expected = [target / name for name in OLIST_FILES]
    if not force and all(p.exists() for p in expected):
        return expected
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "olist.zip"
        fetch(f"{base}/data-v1/olist.zip", archive)
        with zipfile.ZipFile(archive) as zf:
            for member in zf.infolist():
                name = Path(member.filename).name           # flatten any folders inside the zip
                if name in OLIST_FILES:
                    with zf.open(member) as src, open(target / name, "wb") as dst:
                        shutil.copyfileobj(src, dst)
    return expected


def get_taxi(base: str, force: bool) -> list[Path]:
    target = RAW / "taxi"
    expected = [target / name for name in TAXI_FILES] + [target / "taxi_zones" / "taxi_zones.shp"]
    if not force and all(p.exists() for p in expected):
        return expected
    target.mkdir(parents=True, exist_ok=True)
    for name in TAXI_FILES:
        if force or not (target / name).exists():
            fetch(f"{base}/data-v2/{name}", target / name)
    with zipfile.ZipFile(target / "taxi_zones.zip") as zf:
        zf.extractall(target)                                 # creates data/raw/taxi/taxi_zones/
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the course datasets.")
    parser.add_argument("--taxi", action="store_true", help="download the New York taxi data for Project 1")
    parser.add_argument("--force", action="store_true", help="download even if the files exist")
    parser.add_argument("--base-url", default=RELEASES, help=argparse.SUPPRESS)
    args = parser.parse_args()

    name, getter = ("taxi", get_taxi) if args.taxi else ("olist", get_olist)
    try:
        files = getter(args.base_url, args.force)
    except Exception as error:
        print(f"Download failed: {error}", file=sys.stderr)
        print("Check your connection, or ask in the course channel.", file=sys.stderr)
        return 1

    missing = [p for p in files if not p.exists()]
    if missing:
        print("These files are missing after the download:", file=sys.stderr)
        for p in missing:
            print(f"  {p.relative_to(ROOT)}", file=sys.stderr)
        return 1

    print(f"Ready: {name} data in {files[0].parent.relative_to(ROOT)}")
    for p in files:
        print(f"  {str(p.relative_to(files[0].parent)):44} {p.stat().st_size / 1e6:7.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
