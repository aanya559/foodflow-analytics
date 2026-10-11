from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import get_restaurant_performance, get_zone_performance
from src.data_loader import apply_filters, get_filter_options, load_orders_data


def main() -> None:
    st.title("Restaurant & Zone Performance")
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
        st.warning("There is no data after applying the selected filters.")
        return

    restaurant_perf = get_restaurant_performance(filtered, min_sample=10)
    zone_perf = get_zone_performance(filtered, min_sample=15)

    st.subheader("Restaurant performance ranking")
    if restaurant_perf.empty:
        st.info("Not enough restaurant-level sample volume for ranking; widen the date range or reduce filters.")
    else:
        st.dataframe(restaurant_perf, hide_index=True, use_container_width=True)
        st.plotly_chart(px.bar(restaurant_perf, x="restaurant_name", y="late_delivery_rate", title="Restaurant late-delivery rates"), use_container_width=True)

    st.subheader("Delivery-zone comparison")
    if zone_perf.empty:
        st.info("Not enough zone-level sample volume for comparison; widen the reporting window.")
    else:
        st.dataframe(zone_perf, hide_index=True, use_container_width=True)
        st.plotly_chart(px.bar(zone_perf, x="delivery_zone", y="late_delivery_rate", title="Zone late-delivery rates"), use_container_width=True)

    st.subheader("Operational investigation flag")
    if not restaurant_perf.empty:
        flagged_restaurants = restaurant_perf[restaurant_perf["late_delivery_rate"] > restaurant_perf["late_delivery_rate"].quantile(0.75)]
        if flagged_restaurants.empty:
            st.success("No restaurant segment exceeds the investigation threshold in this filtered view.")
        else:
            st.dataframe(flagged_restaurants, hide_index=True, use_container_width=True)

    if not zone_perf.empty:
        flagged_zones = zone_perf[zone_perf["late_delivery_rate"] > zone_perf["late_delivery_rate"].quantile(0.75)]
        if flagged_zones.empty:
            st.success("No delivery zone exceeds the investigation threshold.")
        else:
            st.dataframe(flagged_zones, hide_index=True, use_container_width=True)


main()
