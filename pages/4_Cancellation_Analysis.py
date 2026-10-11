from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analytics import get_cancellation_summary, get_value_outcome_comparison
from src.data_loader import apply_filters, get_filter_options, load_orders_data


def main() -> None:
    st.title("Cancellation Analysis")
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
        st.warning("No rows match this filter set.")
        return

    cancellation_summary = get_cancellation_summary(filtered)
    if cancellation_summary.empty:
        st.info("No cancellations are present in the filtered data.")
    else:
        st.subheader("Cancellation reasons")
        st.dataframe(cancellation_summary, hide_index=True, use_container_width=True)
        st.plotly_chart(px.bar(cancellation_summary, x="cancellation_reason", y="cancelled_orders", title="Cancelled orders by reason"), use_container_width=True)

    st.subheader("Cancellation rate by zone and restaurant")
    zone_cancel = filtered.groupby("delivery_zone")["order_status"].apply(lambda s: (s == "Cancelled").mean()).reset_index(name="cancellation_rate")
    st.dataframe(zone_cancel.sort_values("cancellation_rate", ascending=False), hide_index=True, use_container_width=True)

    restaurant_cancel = filtered.groupby("restaurant_name")["order_status"].apply(lambda s: (s == "Cancelled").mean()).reset_index(name="cancellation_rate")
    st.dataframe(restaurant_cancel.sort_values("cancellation_rate", ascending=False), hide_index=True, use_container_width=True)

    st.subheader("Order-value comparison for completed and cancelled orders")
    outcome_values = get_value_outcome_comparison(filtered)
    st.dataframe(outcome_values, hide_index=True, use_container_width=True)
    st.plotly_chart(px.bar(outcome_values, x="order_status", y="avg_order_value", title="Average order value by outcome"), use_container_width=True)

    st.caption("Observed patterns indicate association, not proof of causation. Use them to guide further investigation and operational testing.")


main()
