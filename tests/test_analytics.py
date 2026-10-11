from __future__ import annotations

import pandas as pd

from scripts.initialize_database import initialize_project_data
from src.analytics import get_daily_order_trends, get_restaurant_performance, get_zone_performance


def test_initialize_project_data_creates_csv_and_database(tmp_path):
    # Use a temporary project path by monkeypatching modules isn't necessary here because the script writes to the workspace root.
    csv_path, db_path = initialize_project_data()
    assert csv_path.exists()
    assert db_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) >= 10000


def test_analytics_helpers_return_expected_shapes():
    csv_path, _ = initialize_project_data()
    df = pd.read_csv(csv_path)

    daily = get_daily_order_trends(df)
    restaurants = get_restaurant_performance(df, min_sample=10)
    zones = get_zone_performance(df, min_sample=15)

    assert not daily.empty
    assert not restaurants.empty
    assert not zones.empty
    assert "late_delivery_rate" in daily.columns
    assert "restaurant_name" in restaurants.columns
    assert "delivery_zone" in zones.columns
