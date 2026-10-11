from __future__ import annotations

import pandas as pd


def late_delivery_flag(row: pd.Series) -> bool:
    """Return True if a completed order was delivered after its estimate."""
    if row.get("order_status") != "Completed":
        return False
    actual = row.get("actual_delivery_minutes")
    estimate = row.get("estimated_delivery_minutes")
    if pd.isna(actual) or pd.isna(estimate):
        return False
    return float(actual) > float(estimate)


def safe_mean(series: pd.Series) -> float:
    if series.empty or series.isna().all():
        return 0.0
    return float(series.dropna().mean())


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    """Calculate core operational KPIs and safe defaults for empty datasets."""
    if df.empty:
        return {
            "total_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "completion_rate": 0.0,
            "cancellation_rate": 0.0,
            "late_deliveries": 0,
            "late_delivery_rate": 0.0,
            "on_time_delivery_rate": 0.0,
            "average_actual_delivery_time": 0.0,
            "average_preparation_time": 0.0,
            "average_delivery_distance": 0.0,
            "average_order_value": 0.0,
            "average_customer_rating": 0.0,
            "estimated_gross_order_value": 0.0,
            "estimated_value_of_cancelled_orders": 0.0,
        }

    total_orders = int(len(df))
    completed_orders = int((df["order_status"] == "Completed").sum())
    cancelled_orders = int((df["order_status"] == "Cancelled").sum())
    completion_rate = completed_orders / total_orders if total_orders else 0.0
    cancellation_rate = cancelled_orders / total_orders if total_orders else 0.0

    completed = df[df["order_status"] == "Completed"].copy()
    valid_completed = completed[
        completed["actual_delivery_minutes"].notna() & completed["estimated_delivery_minutes"].notna()
    ].copy()
    valid_completed["is_late"] = valid_completed.apply(late_delivery_flag, axis=1)
    late_deliveries = int(valid_completed["is_late"].sum())
    late_delivery_rate = late_deliveries / len(valid_completed) if len(valid_completed) else 0.0
    on_time_delivery_rate = 1.0 - late_delivery_rate

    average_actual_delivery_time = safe_mean(valid_completed["actual_delivery_minutes"])
    average_preparation_time = safe_mean(df["preparation_time_minutes"])
    average_delivery_distance = safe_mean(df["delivery_distance_km"])
    average_order_value = safe_mean(df["order_value"])
    average_customer_rating = safe_mean(valid_completed["customer_rating"])
    estimated_gross_order_value = float(df["order_value"].sum())
    estimated_value_of_cancelled_orders = float(
        df.loc[df["order_status"] == "Cancelled", "order_value"].sum()
    )

    return {
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "completion_rate": completion_rate,
        "cancellation_rate": cancellation_rate,
        "late_deliveries": late_deliveries,
        "late_delivery_rate": late_delivery_rate,
        "on_time_delivery_rate": on_time_delivery_rate,
        "average_actual_delivery_time": average_actual_delivery_time,
        "average_preparation_time": average_preparation_time,
        "average_delivery_distance": average_delivery_distance,
        "average_order_value": average_order_value,
        "average_customer_rating": average_customer_rating,
        "estimated_gross_order_value": estimated_gross_order_value,
        "estimated_value_of_cancelled_orders": estimated_value_of_cancelled_orders,
    }
