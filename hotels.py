"""
The hotel booking data: loading, the reference cleaning, the split by booking
date, and the two Block 2 questions. Shared by the Block 2 data notebook and by
every Block 2 lab.

Usage, from inside a folder of the labs repository:

    import sys
    sys.path.insert(0, "..")
    import hotels

    df = hotels.block_2()                 # loaded, cleaned, split by booking date
    cancel = hotels.cancellation(df)      # one question's population, with `target`
    rate = hotels.daily_rate(df)          # the other one

Pass `sample=` to thin each split while you are developing:

    df = hotels.block_2(sample=20_000)

Source: Antonio, Almeida and Nunes (2019), "Hotel booking demand datasets",
Data in Brief 22, 41-49. Two Portuguese hotels, arrivals July 2015 to August
2017. CC BY 4.0. https://doi.org/10.1016/j.dib.2018.11.126
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parent / "data" / "raw" / "hotels"
BOOKINGS_FILE = RAW / "hotel_bookings.parquet"

MONTHS = {name: number for number, name in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}

# Split by the day the booking was made, not the day of arrival: at the moment
# we predict, the arrival has not happened yet.
SPLIT_DATES = ("2016-10-01", "2017-01-01")

# A nightly rate outside this is either an error or a booking of a kind the
# model is not being asked about. Applied only to the rate question.
ADR_RANGE = (1.0, 1000.0)

# Columns that exist in the file but not at the moment of booking.
#   reservation_status      is the target wearing a different hat
#   reservation_status_date is when that status was set
#   assigned_room_type      is decided at check-in
#   booking_changes         accumulates after the booking is made
#   days_in_waiting_list    is known only once the wait is over
NOT_KNOWN_AT_BOOKING = [
    "reservation_status", "reservation_status_date", "assigned_room_type",
    "booking_changes", "days_in_waiting_list",
]

# The columns every Block 2 lab starts from, so that each week compares like
# with like. What you build on top of them is yours.
AT_BOOKING_NUMERIC = [
    "lead_time", "stays_in_weekend_nights", "stays_in_week_nights",
    "total_nights", "adults", "children", "babies", "total_guests",
    "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "required_car_parking_spaces",
    "total_of_special_requests", "arrival_month", "arrival_week",
    "arrival_day",
]
AT_BOOKING_CATEGORICAL = [
    "hotel", "meal", "country", "market_segment", "distribution_channel",
    "reserved_room_type", "deposit_type", "agent", "company", "customer_type",
]


def _check_data() -> None:
    if not BOOKINGS_FILE.exists():
        raise FileNotFoundError(
            f"No hotel data at {RAW}. From the repository root, run: "
            "python data/download.py --hotels"
        )


# --- Loading ------------------------------------------------------------------------


def load_bookings() -> pd.DataFrame:
    """The published file, untouched, plus the dates and totals every lab needs.

    Adds: arrival_date, booking_date (arrival minus the lead time, which is when
    the booking was actually made), total_nights, total_guests, and numeric
    arrival_month / arrival_week / arrival_day.
    """
    _check_data()
    df = pd.read_parquet(BOOKINGS_FILE)

    df["arrival_month"] = df["arrival_date_month"].map(MONTHS)
    df["arrival_week"] = df["arrival_date_week_number"]
    df["arrival_day"] = df["arrival_date_day_of_month"]
    df["arrival_date"] = pd.to_datetime(dict(
        year=df["arrival_date_year"], month=df["arrival_month"],
        day=df["arrival_day"]), errors="coerce")
    df["booking_date"] = df["arrival_date"] - pd.to_timedelta(df["lead_time"], unit="D")

    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_guests"] = df[["adults", "children", "babies"]].fillna(0).sum(axis=1)

    # agent and company are identifiers, not quantities. Missing means "booked
    # directly", which is information, so it gets a name rather than a gap.
    for column in ("agent", "company"):
        df[column] = df[column].astype("string").fillna("none")

    return df


# --- The reference cleaning ---------------------------------------------------------


def cleaning_rules(df: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    """Each rule names a kind of booking that cannot be real, and marks those rows.

    Deliberately short. These are not judgement calls: a booking with nobody in
    it, or no nights in it, or a negative price, is a recording error whichever
    question you are answering. Everything debatable is left for you to decide.
    """
    return [
        ("nobody in the booking", df["total_guests"] == 0),
        ("no nights booked", df["total_nights"] == 0),
        ("a negative nightly rate", df["adr"] < 0),
    ]


def clean_bookings(df: pd.DataFrame, log: bool = False):
    """Remove bookings that cannot be real, and fix one recording habit.

    Removes: bookings with no guests, no nights, or a negative rate (826 rows).

    Fixes: `meal` records self-catering as both "SC" and "Undefined"; both mean
    the same thing, so "Undefined" becomes "SC".

    Nothing here learns from the data, so it is safe to run before the split.
    With log=True, also returns how many bookings each rule removed.
    """
    keep = pd.Series(True, index=df.index)
    rows = []
    for name, bad in cleaning_rules(df):
        removed = int((keep & bad).sum())
        keep &= ~bad
        rows.append({"rule": name, "removed": removed, "remaining": int(keep.sum())})

    clean = df[keep].copy()
    clean["meal"] = clean["meal"].replace("Undefined", "SC")
    clean = clean.reset_index(drop=True)

    if log:
        return clean, pd.DataFrame(rows).set_index("rule")
    return clean


def split_by_booking_date(df: pd.DataFrame) -> pd.DataFrame:
    """Bookings made before October 2016 train, the next three months validate,
    everything booked in 2017 tests once.

    Arrival periods overlap across the splits, because a booking made in
    September 2016 can be for an arrival in 2017. That is correct: we are
    predicting at the moment of booking, so what matters is when we would have
    known about the booking, not when the guest turns up.
    """
    df = df.copy()
    first, second = pd.Timestamp(SPLIT_DATES[0]), pd.Timestamp(SPLIT_DATES[1])
    df["split"] = np.select(
        [df["booking_date"] < first, df["booking_date"] < second],
        ["train", "valid"], default="test")
    return df


def bookings() -> pd.DataFrame:
    """The starting table for both questions: loaded, cleaned, split."""
    return split_by_booking_date(clean_bookings(load_bookings()))


# --- The two questions --------------------------------------------------------------


def cancellation(df: pd.DataFrame) -> pd.DataFrame:
    """Will this booking be cancelled? Every booking counts, `target` is 0 or 1.

    The nightly rate is agreed when the booking is made, so `adr` is allowed
    here as a feature.
    """
    out = df.copy()
    out["target"] = out["is_canceled"].astype(int)
    return out.drop(columns=NOT_KNOWN_AT_BOOKING, errors="ignore")


def daily_rate(df: pd.DataFrame) -> pd.DataFrame:
    """What will this booking pay per night? `target` is the rate in euros.

    Keeps rates inside ADR_RANGE. A rate of exactly 0 is a real thing in this
    data (complimentary and some group bookings, about 1,900 of them) but it is
    a different question, so it is left out rather than predicted.

    Whether the booking was later cancelled is not known at booking, so
    `is_canceled` goes out along with the rest.
    """
    out = df[df["adr"].between(*ADR_RANGE)].copy()
    out["target"] = out["adr"]
    return out.drop(columns=NOT_KNOWN_AT_BOOKING + ["is_canceled", "adr"],
                    errors="ignore").reset_index(drop=True)


# --- What every Block 2 lab starts from ----------------------------------------------


def splits(df: pd.DataFrame, sample: int | None = None, seed: int = 42):
    """Return (train, valid, test). With `sample`, take that many rows from each,
    which keeps a lab responsive on a laptop. Page numbers use the full splits."""
    parts = []
    for name in ("train", "valid", "test"):
        part = df[df["split"] == name]
        if sample is not None and sample < len(part):
            part = part.sample(sample, random_state=seed)
        parts.append(part)
    return tuple(parts)


def block_2(sample: int | None = None, seed: int = 42) -> pd.DataFrame:
    """The starting table for every Block 2 lab: cleaned and split, with the
    derived dates and totals. Pass `sample` to thin each split for a faster lab."""
    df = bookings()
    if sample is None:
        return df
    return pd.concat(splits(df, sample=sample, seed=seed), ignore_index=True)


def features(df: pd.DataFrame) -> pd.DataFrame:
    """Just the at-booking columns, in a fixed order, so weeks compare like with like."""
    return df[AT_BOOKING_NUMERIC + AT_BOOKING_CATEGORICAL]


def baseline(train: pd.DataFrame, valid: pd.DataFrame, task: str) -> dict:
    """The floor a model has to clear, computed on the training rows only.

    task="cancellation": the share of bookings cancelled, which is what PR AUC
    scores when the model has no skill. Lift is PR AUC divided by it.

    task="rate": predicting the training mean for everyone, scored on valid.
    """
    if task == "cancellation":
        rate = float(train["target"].mean())
        return {"positive_rate": rate, "pr_auc_floor": rate, "lift_floor": 1.0}
    guess = float(train["target"].mean())
    error = (valid["target"] - guess).abs()
    return {"mean": guess, "r2_floor": 0.0, "mae_floor": float(error.mean())}
