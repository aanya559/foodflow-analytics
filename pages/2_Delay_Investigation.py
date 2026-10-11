from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import get_time_of_day_summary, get_traffic_weather_comparison
from src.data_loader import apply_filters, get_filter_options, load_orders_data
from src.visualizations import chart_late_hours, chart_prep_vs_delivery


def main() -> None:
    st.title("Delay Investigation")
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
        st.warning("No rows match the current filters.")
        return

    completed = filtered[filtered["order_status"] == "Completed"].copy()
    completed["delay_minutes"] = completed["actual_delivery_minutes"] - completed["estimated_delivery_minutes"]

    st.subheader("Delivery-time distribution")
    hist = px.histogram(completed, x="delay_minutes", nbins=30, title="Delay distribution in minutes")
    st.plotly_chart(hist, use_container_width=True)

    st.subheader("Actual versus estimated delivery time")
    scatter = px.scatter(
        completed,
        x="estimated_delivery_minutes",
        y="actual_delivery_minutes",
        color="traffic_level",
        title="Actual vs estimated delivery time",
        opacity=0.6,
    )
    st.plotly_chart(scatter, use_container_width=True)

    hour_summary = get_time_of_day_summary(filtered)
    st.subheader("Late-delivery rate by hour")
    st.plotly_chart(px.bar(hour_summary, x="hour_of_day", y="late_delivery_rate", title="Late-delivery rate by hour of day"), use_container_width=True)

    st.subheader("Delay comparisons by traffic and weather")
    traffic_weather = get_traffic_weather_comparison(filtered)
    st.plotly_chart(px.bar(traffic_weather, x="traffic_level", y="late_delivery_rate", color="weather_condition", barmode="group", title="Late-delivery rate by traffic and weather"), use_container_width=True)

    st.subheader("Preparation time versus delivery time")
    st.plotly_chart(chart_prep_vs_delivery(filtered), use_container_width=True)

    st.subheader("Delay breakdown by distance band")
    completed["distance_band"] = pd.cut(completed["delivery_distance_km"], bins=[0, 2, 5, 8, 12, 20], labels=["0-2 km", "2-5 km", "5-8 km", "8-12 km", "12+ km"])
    delay_by_distance = completed.groupby("distance_band")["delay_minutes"].mean().reset_index(name="avg_delay_minutes")
    st.plotly_chart(px.bar(delay_by_distance, x="distance_band", y="avg_delay_minutes", title="Average delay by distance band"), use_container_width=True)

    st.subheader("Most delayed orders")
    most_delayed = completed.sort_values("delay_minutes", ascending=False).head(10)[["order_id", "restaurant_name", "delivery_zone", "delay_minutes", "estimated_delivery_minutes", "actual_delivery_minutes", "traffic_level", "weather_condition"]]
    st.dataframe(most_delayed, hide_index=True, use_container_width=True)


main()
