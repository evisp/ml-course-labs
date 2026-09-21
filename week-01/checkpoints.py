"""
Starting tables for each week, rebuilt from the raw Olist files.

Every lab from Week 2 onwards begins with one of these, so you can start any
week even if you missed the one before. Each function takes a few seconds and
always gives the same result as that week's solution notebook.

Usage, from inside a week folder:

    import sys
    sys.path.append("..")
    from checkpoints import week_01

    orders = week_01()
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent / "data" / "raw" / "olist"

# The usable window. Months before 2017 and after August 2018 have almost no
# orders, and none of the late-2018 ones were ever delivered.
START = "2017-01-01"
END = "2018-09-01"

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def _check_data() -> None:
    if not RAW.exists():
        raise FileNotFoundError(
            f"No data at {RAW}. Run `python data/download.py` from the repository root first."
        )


def week_01() -> pd.DataFrame:
    """Delivered orders in the usable window, with the customer's state and the
    is_late target. One row per order.

    is_late is 1 when the order arrived on a later calendar day than promised.
    Orders that were never delivered are left out, because we cannot label them.
    """
    _check_data()
    orders = pd.read_csv(RAW / "olist_orders_dataset.csv", parse_dates=DATE_COLUMNS)
    customers = pd.read_csv(RAW / "olist_customers_dataset.csv")

    df = orders.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")

    delivered = df["order_delivered_customer_date"].notna()
    in_window = df["order_purchase_timestamp"].between(START, END, inclusive="left")
    df = df[delivered & in_window].copy()

    delivered_day = df["order_delivered_customer_date"].dt.normalize()
    df["is_late"] = (delivered_day > df["order_estimated_delivery_date"]).astype(int)

    return df.sort_values("order_purchase_timestamp").reset_index(drop=True)
