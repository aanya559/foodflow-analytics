from __future__ import annotations

import streamlit as st

from src.data_loader import apply_filters, get_filter_options, load_orders_data
from src.insights import generate_recommendations
from src.kpi_calculations import calculate_kpis


def main() -> None:
    st.title("Business Recommendations")
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
        st.warning("The selected filters produce no rows. Expand the date range or remove one or more filters to generate recommendations.")
        return

    kpis = calculate_kpis(filtered)
    recommendations = generate_recommendations(filtered, kpis)

    st.subheader("Evidence-based recommendations")
    for index, rec in enumerate(recommendations, start=1):
        with st.container():
            st.markdown(f"### {index}. {rec['metric']}")
            st.markdown(f"- **Observed metric:** {rec['metric']}")
            st.markdown(f"- **Comparison / benchmark:** {rec['benchmark']}")
            st.markdown(f"- **Why it matters:** {rec['why']}")
            st.markdown(f"- **Practical next step:** {rec['next_step']}")
            st.write("---")

    st.caption("The recommendation engine is evidence-driven and uses only calculated metrics from the filtered dataset; it does not assert causality without supporting evidence.")


main()
