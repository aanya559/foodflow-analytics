from __future__ import annotations

import streamlit as st

from src.data_loader import ensure_project_data

st.set_page_config(layout="wide", page_title="FoodFlow Analytics")

ensure_project_data()

pages = [
    st.Page("pages/1_Executive_Overview.py", title="Executive Overview", icon="📊"),
    st.Page("pages/2_Delay_Investigation.py", title="Delay Investigation", icon="⏱️"),
    st.Page("pages/3_Restaurant_Zone_Performance.py", title="Restaurant & Zone Performance", icon="🏪"),
    st.Page("pages/4_Cancellation_Analysis.py", title="Cancellation Analysis", icon="🚫"),
    st.Page("pages/5_Business_Recommendations.py", title="Business Recommendations", icon="💡"),
]

navigation = st.navigation(pages)
navigation.run()
