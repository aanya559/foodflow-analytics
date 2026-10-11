from __future__ import annotations

from typing import Any

import pandas as pd


def validate_orders(df: pd.DataFrame) -> dict[str, Any]:
    """Return a summary of data-quality issues in the dataset."""
    if df.empty:
        return {
            "missing_values": {},
            "duplicate_rows": 0,
            "invalid_durations": 0,
            "inconsistent_statuses": 0,
            "invalid_numerics": 0,
            "issues": ["Dataset is empty."],
        }

    missing_values = df.isna().sum().to_dict()
    duplicate_rows = int(df.duplicated(subset=["order_id"]).sum())

    invalid_duration_mask = (
        (df["preparation_time_minutes"] <= 0)
        | (df["estimated_delivery_minutes"] <= 0)
        | (df["delivery_distance_km"] <= 0)
        | (df["order_value"] <= 0)
    )
    invalid_durations = int(invalid_duration_mask.sum())

    completed = df[df["order_status"] == "Completed"]
    invalid_completed_delivery = int(
        (
            completed["actual_delivery_minutes"].isna()
            | (completed["actual_delivery_minutes"] <= 0)
        ).sum()
    )

    cancelled = df[df["order_status"] == "Cancelled"]
    cancelled_without_reason = int(
        cancelled["cancellation_reason"].fillna("").str.strip().eq("").sum()
    )

    inconsistent_statuses = invalid_completed_delivery + cancelled_without_reason

    invalid_numerics = int(
        (
            df[["preparation_time_minutes", "estimated_delivery_minutes", "actual_delivery_minutes", "delivery_distance_km", "order_value", "customer_rating"]]
            .apply(lambda col: (col < 0).sum())
            .sum()
        )
    )

    issues = []
    if duplicate_rows:
        issues.append(f"{duplicate_rows} duplicated order IDs found.")
    if invalid_durations:
        issues.append(f"{invalid_durations} rows have invalid duration or distance values.")
    if inconsistent_statuses:
        issues.append(f"{inconsistent_statuses} rows have inconsistent order-status data.")
    if invalid_numerics:
        issues.append(f"{invalid_numerics} negative numerical values found.")

    return {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "invalid_durations": invalid_durations,
        "inconsistent_statuses": inconsistent_statuses,
        "invalid_numerics": invalid_numerics,
        "issues": issues,
    }


def clean_duplicate_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows while preserving the first valid record."""
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates(subset=["order_id"], keep="first")
    return cleaned


def validate_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply cleaning steps and return the cleaned data plus validation summary."""
    cleaned = clean_duplicate_orders(df)
    summary = validate_orders(cleaned)
    return cleaned, summary
