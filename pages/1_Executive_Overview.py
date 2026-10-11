from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import build_export_frames, get_daily_order_trends
from src.data_loader import ensure_project_data, load_orders_data, apply_filters, get_filter_options
from src.insights import generate_recommendations
from src.kpi_calculations import calculate_kpis
from src.visualizations import chart_daily_orders


st.set_page_config(layout="wide")
ensure_project_data()


def main() -> None:
    st.title("Executive Overview")
    st.caption("Synthetic food-delivery operations dataset for evidence-based operational analysis.")

    orders = load_orders_data()
    options = get_filter_options(orders)

    with st.sidebar:
        st.header("Filters")
        start_date = st.date_input("Start date", min_value=orders["order_date"].min().date(), max_value=orders["order_date"].max().date(), value=orders["order_date"].min().date())
        end_date = st.date_input("End date", min_value=orders["order_date"].min().date(), max_value=orders["order_date"].max().date(), value=orders["order_date"].max().date())
        selected_zone = st.multiselect("Delivery zone", options["zones"], default=options["zones"])
        selected_restaurant = st.multiselect("Restaurant", options["restaurants"], default=options["restaurants"])
        selected_traffic = st.multiselect("Traffic level", options["traffic_levels"], default=options["traffic_levels"])
        selected_weather = st.multiselect("Weather condition", options["weather_conditions"], default=options["weather_conditions"])
        selected_status = st.multiselect("Order status", options["order_status"], default=options["order_status"])

    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "zone": selected_zone,
        "restaurant": selected_restaurant,
        "traffic_level": selected_traffic,
        "weather_condition": selected_weather,
        "order_status": selected_status,
    }
    filtered = apply_filters(orders, filters)

    if filtered.empty:
        st.warning("No rows match the selected filters. Adjust the filters to view performance metrics.")
        return

    kpis = calculate_kpis(filtered)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total orders", int(kpis["total_orders"]))
    metric_cols[1].metric("Completion rate", f"{kpis['completion_rate']:.1%}")
    metric_cols[2].metric("Cancellation rate", f"{kpis['cancellation_rate']:.1%}")
    metric_cols[3].metric("Late-delivery rate", f"{kpis['late_delivery_rate']:.1%}")

    secondary_cols = st.columns(4)
    secondary_cols[0].metric("Avg delivery time", f"{kpis['average_actual_delivery_time']:.1f} min")
    secondary_cols[1].metric("Avg preparation", f"{kpis['average_preparation_time']:.1f} min")
    secondary_cols[2].metric("Avg order value", f"${kpis['average_order_value']:.2f}")
    secondary_cols[3].metric("Cancelled order value", f"${kpis['estimated_value_of_cancelled_orders']:.2f}")

    trend_df = get_daily_order_trends(filtered)
    chart_df = trend_df.copy()
    chart_df["late_delivery_rate"] = (chart_df["late_orders"] / chart_df["total_orders"]).fillna(0)
    st.subheader("Daily order volume and late-delivery trends")
    fig = px.line(chart_df, x="order_date", y=["total_orders", "late_orders"], markers=True, title="Orders and late deliveries by day")
    st.plotly_chart(fig, use_container_width=True)

    left_col, right_col = st.columns(2)
    with left_col:
        status_counts = filtered["order_status"].value_counts().reset_index()
        status_counts.columns = ["order_status", "orders"]
        status_fig = px.pie(status_counts, names="order_status", values="orders", title="Completed vs cancelled orders")
        st.plotly_chart(status_fig, use_container_width=True)
    with right_col:
        order_value_by_status = filtered.groupby("order_status")["order_value"].mean().reset_index()
        order_fig = px.bar(order_value_by_status, x="order_status", y="order_value", title="Average order value by outcome")
        st.plotly_chart(order_fig, use_container_width=True)

    export_frames = build_export_frames(filtered)
    download_cols = st.columns(4)
    download_cols[0].download_button(
        "Download filtered orders",
        export_frames["orders"].to_csv(index=False),
        file_name="filtered_orders.csv",
        mime="text/csv",
    )
    download_cols[1].download_button(
        "Download restaurant performance",
        export_frames["restaurant_performance"].to_csv(index=False),
        file_name="restaurant_performance.csv",
        mime="text/csv",
    )
    download_cols[2].download_button(
        "Download zone performance",
        export_frames["zone_performance"].to_csv(index=False),
        file_name="zone_performance.csv",
        mime="text/csv",
    )
    download_cols[3].download_button(
        "Download KPI summary",
        export_frames["kpis"].to_csv(index=False),
        file_name="kpi_summary.csv",
        mime="text/csv",
    )

    recommendations = generate_recommendations(filtered, kpis)
    st.subheader("Automatically generated insights")
    for rec in recommendations:
        with st.container():
            st.markdown(f"- **{rec['metric']}** — benchmark: {rec['benchmark']} | why: {rec['why']} | next step: {rec['next_step']}")


main()
