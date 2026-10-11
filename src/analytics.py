from __future__ import annotations

import pandas as pd

from .kpi_calculations import calculate_kpis, late_delivery_flag


def enrich_order_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    orders = df.copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["hour_of_day"] = pd.to_datetime(orders["order_time"], format="%H:%M").dt.hour
    orders["is_late"] = orders.apply(late_delivery_flag, axis=1)
    return orders


def get_daily_order_trends(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["order_date", "total_orders", "late_orders", "cancelled_orders"])
    summary = orders.groupby("order_date").agg(
        total_orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
        cancelled_orders=("order_status", lambda s: (s == "Cancelled").sum()),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["total_orders"]
    return summary


def get_restaurant_performance(df: pd.DataFrame, min_sample: int = 10) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["restaurant_name", "total_orders", "completion_rate", "late_delivery_rate", "avg_preparation_time", "avg_delivery_time"])
    completed = orders[orders["order_status"] == "Completed"].copy()
    summary = completed.groupby("restaurant_name").agg(
        total_orders=("order_id", "count"),
        avg_preparation_time=("preparation_time_minutes", "mean"),
        avg_delivery_time=("actual_delivery_minutes", "mean"),
        late_count=("is_late", "sum"),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_count"] / summary["total_orders"]
    summary["completion_rate"] = (
        orders.groupby("restaurant_name")["order_status"].apply(lambda s: (s == "Completed").mean())
    ).reset_index(name="completion_rate")["completion_rate"]
    summary = summary[summary["total_orders"] >= min_sample].sort_values("late_delivery_rate", ascending=False)
    return summary


def get_zone_performance(df: pd.DataFrame, min_sample: int = 15) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["delivery_zone", "total_orders", "late_delivery_rate", "avg_delivery_time", "avg_preparation_time"])
    summary = orders.groupby("delivery_zone").agg(
        total_orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
        avg_preparation_time=("preparation_time_minutes", "mean"),
        avg_delivery_time=("actual_delivery_minutes", "mean"),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["total_orders"]
    summary = summary[summary["total_orders"] >= min_sample].sort_values("late_delivery_rate", ascending=False)
    return summary


def get_cancellation_summary(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["cancellation_reason", "cancelled_orders", "cancellation_rate"])
    cancelled = orders[orders["order_status"] == "Cancelled"].copy()
    summary = cancelled.groupby("cancellation_reason").size().reset_index(name="cancelled_orders")
    total_cancelled = summary["cancelled_orders"].sum()
    if total_cancelled:
        summary["cancellation_rate"] = summary["cancelled_orders"] / total_cancelled
    else:
        summary["cancellation_rate"] = 0.0
    return summary.sort_values("cancelled_orders", ascending=False)


def get_partner_performance(df: pd.DataFrame, min_sample: int = 20) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["delivery_partner_id", "completed_deliveries", "avg_customer_rating", "late_delivery_rate"])
    completed = orders[orders["order_status"] == "Completed"].copy()
    summary = completed.groupby("delivery_partner_id").agg(
        completed_deliveries=("order_id", "count"),
        avg_customer_rating=("customer_rating", "mean"),
        late_orders=("is_late", "sum"),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["completed_deliveries"]
    summary = summary[summary["completed_deliveries"] >= min_sample].sort_values("late_delivery_rate", ascending=False)
    return summary


def get_time_of_day_summary(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["hour_of_day", "total_orders", "late_delivery_rate"])
    summary = orders.groupby("hour_of_day").agg(
        total_orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["total_orders"]
    return summary.sort_values("hour_of_day")


def get_value_outcome_comparison(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["order_status", "avg_order_value", "total_value", "order_count"])
    summary = orders.groupby("order_status").agg(
        avg_order_value=("order_value", "mean"),
        total_value=("order_value", "sum"),
        order_count=("order_id", "count"),
    ).reset_index()
    return summary


def get_traffic_weather_comparison(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["traffic_level", "weather_condition", "total_orders", "late_delivery_rate"]) 
    summary = orders.groupby(["traffic_level", "weather_condition"]).agg(
        total_orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
    ).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["total_orders"]
    return summary.sort_values("late_delivery_rate", ascending=False)


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["column", "missing_values"])
    missing = df.isna().sum().reset_index()
    missing.columns = ["column", "missing_values"]
    return missing[missing["missing_values"] > 0].sort_values("missing_values", ascending=False)


def get_duplicate_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["duplicate_order_ids", "count"])
    duplicates = df[df.duplicated(subset=["order_id"], keep=False)]
    return duplicates.groupby("order_id").size().reset_index(name="count").rename(columns={"order_id": "duplicate_order_ids"})


def get_descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    if not numeric_columns:
        return pd.DataFrame(columns=["metric", "value"])
    summary = df[numeric_columns].describe().T.reset_index().rename(columns={"index": "metric"})
    return summary


def get_correlation_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return pd.DataFrame(columns=["column_a", "column_b", "correlation"])
    corr_matrix = numeric_df.corr().stack().reset_index()
    corr_matrix.columns = ["column_a", "column_b", "correlation"]
    corr_matrix = corr_matrix[corr_matrix["column_a"] != corr_matrix["column_b"]]
    return corr_matrix.sort_values("correlation", ascending=False)


def get_grouped_comparison(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[group_col, value_col])
    return df.groupby(group_col)[value_col].mean().reset_index()


def get_time_trend_summary(df: pd.DataFrame) -> pd.DataFrame:
    orders = enrich_order_features(df)
    if orders.empty:
        return pd.DataFrame(columns=["order_date", "total_orders", "late_delivery_rate"])
    summary = orders.groupby("order_date").agg(total_orders=("order_id", "count"), late_orders=("is_late", "sum")).reset_index()
    summary["late_delivery_rate"] = summary["late_orders"] / summary["total_orders"]
    return summary


def build_export_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    filtered = df.copy()
    if filtered.empty:
        return {
            "orders": pd.DataFrame(columns=["order_id", "restaurant_name", "delivery_zone", "order_status", "order_value", "actual_delivery_minutes"]),
            "restaurant_performance": pd.DataFrame(columns=["restaurant_name", "total_orders", "late_delivery_rate"]),
            "zone_performance": pd.DataFrame(columns=["delivery_zone", "total_orders", "late_delivery_rate"]),
            "kpis": pd.DataFrame([calculate_kpis(filtered)], index=[0]),
        }

    orders_export = filtered[[
        "order_id",
        "order_date",
        "order_time",
        "restaurant_name",
        "delivery_zone",
        "order_status",
        "order_value",
        "preparation_time_minutes",
        "estimated_delivery_minutes",
        "actual_delivery_minutes",
        "weather_condition",
        "traffic_level",
        "customer_rating",
    ]].copy()

    restaurant_export = get_restaurant_performance(filtered, min_sample=10)
    zone_export = get_zone_performance(filtered, min_sample=15)
    kpi_export = pd.DataFrame([calculate_kpis(filtered)])

    return {
        "orders": orders_export,
        "restaurant_performance": restaurant_export,
        "zone_performance": zone_export,
        "kpis": kpi_export,
    }
