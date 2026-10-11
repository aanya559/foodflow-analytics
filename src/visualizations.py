from __future__ import annotations

import plotly.express as px
import pandas as pd


def chart_daily_orders(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"order_date": [], "total_orders": []}), x="order_date", y="total_orders")
    chart_df = df.groupby("order_date").agg(total_orders=("order_id", "count")).reset_index()
    return px.line(chart_df, x="order_date", y="total_orders", markers=True, title="Daily order volume")


def chart_late_hours(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"hour": [], "late_delivery_rate": []}), x="hour", y="late_delivery_rate")
    if "hour_of_day" not in df.columns:
        df = df.copy()
        df["hour_of_day"] = pd.to_datetime(df["order_time"], format="%H:%M").dt.hour
    summary = df.groupby("hour_of_day").apply(lambda s: (s["is_late"].mean() if "is_late" in s.columns else 0)).reset_index(name="late_delivery_rate")
    summary.columns = ["hour_of_day", "late_delivery_rate"]
    return px.bar(summary, x="hour_of_day", y="late_delivery_rate", title="Late-delivery rate by hour")


def chart_prep_vs_delivery(df: pd.DataFrame):
    if df.empty:
        return px.scatter(pd.DataFrame({"preparation_time_minutes": [], "actual_delivery_minutes": []}), x="preparation_time_minutes", y="actual_delivery_minutes")
    data = df[df["order_status"] == "Completed"].copy()
    return px.scatter(
        data,
        x="preparation_time_minutes",
        y="actual_delivery_minutes",
        color="traffic_level",
        opacity=0.5,
        title="Preparation time vs delivery time",
    )


def chart_cancel_reasons(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"cancellation_reason": [], "cancelled_orders": []}), x="cancellation_reason", y="cancelled_orders")
    summary = df[df["order_status"] == "Cancelled"].groupby("cancellation_reason").size().reset_index(name="cancelled_orders")
    return px.bar(summary, x="cancellation_reason", y="cancelled_orders", title="Cancellation reasons")


def chart_zone_comparison(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"delivery_zone": [], "late_delivery_rate": []}), x="delivery_zone", y="late_delivery_rate")
    summary = df.groupby("delivery_zone").apply(lambda s: (s["is_late"].mean() if "is_late" in s.columns else 0)).reset_index(name="late_delivery_rate")
    summary.columns = ["delivery_zone", "late_delivery_rate"]
    return px.bar(summary, x="delivery_zone", y="late_delivery_rate", color="delivery_zone", title="Late-delivery rate by zone")


def chart_order_value_by_status(df: pd.DataFrame):
    if df.empty:
        return px.bar(pd.DataFrame({"order_status": [], "avg_order_value": []}), x="order_status", y="avg_order_value")
    summary = df.groupby("order_status")["order_value"].mean().reset_index(name="avg_order_value")
    return px.bar(summary, x="order_status", y="avg_order_value", title="Average order value by outcome")
