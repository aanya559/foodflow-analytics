from __future__ import annotations

from typing import Any

import pandas as pd


def generate_recommendations(df: pd.DataFrame, kpis: dict[str, Any]) -> list[dict[str, str]]:
    """Generate data-driven recommendations for the current filtered order set."""
    if df.empty:
        return [{
            "metric": "Insufficient evidence",
            "benchmark": "More data is required",
            "why": "The current data slice has no rows after filters are applied.",
            "next_step": "Expand the date range or remove a filter to gather enough evidence.",
        }]

    orders = df.copy()
    if "is_late" not in orders.columns:
        orders["is_late"] = orders.apply(
            lambda row: row["order_status"] == "Completed" and row["actual_delivery_minutes"] > row["estimated_delivery_minutes"], axis=1
        )
    overall_late_rate = float(kpis.get("late_delivery_rate", 0.0))
    zone_summary = orders.groupby("delivery_zone").apply(lambda s: float(s["is_late"].mean()) if "is_late" in s.columns else 0.0).reset_index(name="late_rate")
    zone_summary.columns = ["delivery_zone", "late_rate"]
    worst_zone = zone_summary.sort_values("late_rate", ascending=False).head(1)
    recommendations = []

    if not worst_zone.empty and worst_zone.iloc[0]["late_rate"] > max(overall_late_rate + 0.05, 0.12):
        zone_name = worst_zone.iloc[0]["delivery_zone"]
        recommendations.append({
            "metric": f"Late-delivery rate in {zone_name}",
            "benchmark": f">{overall_late_rate:.1%} overall rate",
            "why": "This zone is materially worse than the overall service baseline and may reflect routing, traffic, or dispatch inefficiency.",
            "next_step": "Review real-time route planning and staffing for this zone during peak periods.",
        })

    if "preparation_time_minutes" in orders.columns:
        prep_by_restaurant = orders.groupby("restaurant_name")["preparation_time_minutes"].mean()
        high_prep = prep_by_restaurant.sort_values(ascending=False).head(1)
        if not high_prep.empty and float(high_prep.iloc[0]) > float(orders["preparation_time_minutes"].mean()) * 1.2:
            restaurant_name = high_prep.index[0]
            recommendations.append({
                "metric": f"Preparation time at {restaurant_name}",
                "benchmark": f">{orders['preparation_time_minutes'].mean():.1f} min average",
                "why": "Long preparation windows are a strong upstream driver of late deliveries and can create downstream capacity issues.",
                "next_step": "Review kitchen staffing, peak-hour order batching, and menu complexity for this restaurant.",
            })

    if "hour_of_day" not in orders.columns:
        orders["hour_of_day"] = pd.to_datetime(orders["order_time"], format="%H:%M").dt.hour
    peak_hour = orders.groupby("hour_of_day").agg(total_orders=("order_id", "count"), late_rate=("is_late", "mean")).sort_values(["total_orders", "late_rate"], ascending=False).head(1)
    if not peak_hour.empty and float(peak_hour.iloc[0]["total_orders"]) > max(1, len(orders) * 0.05):
        hour_value = int(peak_hour.index[0])
        recommendations.append({
            "metric": f"Peak-hour demand at {hour_value}:00",
            "benchmark": f">5% of total orders and elevated late rate",
            "why": "Demand surges can overwhelm both restaurant kitchens and delivery networks, creating compounding delays.",
            "next_step": "Add staffing or adjust dispatch windows around this hour to reduce congestion.",
        })

    cancellation_summary = orders[orders["order_status"] == "Cancelled"].groupby("cancellation_reason").size()
    if not cancellation_summary.empty:
        top_reason = cancellation_summary.sort_values(ascending=False).head(1)
        recommendations.append({
            "metric": f"Top cancellation reason: {top_reason.index[0]}",
            "benchmark": f"{top_reason.iloc[0]} cancelled orders",
            "why": "The largest cancellation signal should be addressed before proposing broad operational changes, because it indicates a recurring friction point.",
            "next_step": "Investigate the most common rejection cause with operational staff and customer feedback analysis.",
        })

    if not recommendations:
        recommendations.append({
            "metric": "No major operational outliers",
            "benchmark": "All KPIs are within a stable operating band",
            "why": "The filtered dataset does not show a clear operational issue strong enough to justify a tactical intervention.",
            "next_step": "Continue monitoring during the next reporting cycle to confirm trends before making structural changes.",
        })

    return recommendations
