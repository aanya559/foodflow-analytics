from __future__ import annotations

import pandas as pd

from src.kpi_calculations import calculate_kpis, late_delivery_flag


def test_late_delivery_flag_classifies_completed_orders():
    row = pd.Series({
        "order_status": "Completed",
        "actual_delivery_minutes": 42,
        "estimated_delivery_minutes": 30,
    })
    assert late_delivery_flag(row) is True

    cancelled_row = pd.Series({
        "order_status": "Cancelled",
        "actual_delivery_minutes": 60,
        "estimated_delivery_minutes": 30,
    })
    assert late_delivery_flag(cancelled_row) is False


def test_calculate_kpis_handles_sample_dataset():
    df = pd.DataFrame(
        [
            {
                "order_id": "A1",
                "order_status": "Completed",
                "actual_delivery_minutes": 50,
                "estimated_delivery_minutes": 40,
                "preparation_time_minutes": 15,
                "delivery_distance_km": 5,
                "order_value": 20,
                "customer_rating": 4.5,
            },
            {
                "order_id": "A2",
                "order_status": "Completed",
                "actual_delivery_minutes": 25,
                "estimated_delivery_minutes": 30,
                "preparation_time_minutes": 10,
                "delivery_distance_km": 3,
                "order_value": 15,
                "customer_rating": 4.0,
            },
            {
                "order_id": "A3",
                "order_status": "Cancelled",
                "actual_delivery_minutes": None,
                "estimated_delivery_minutes": 35,
                "preparation_time_minutes": 12,
                "delivery_distance_km": 2,
                "order_value": 35,
                "customer_rating": None,
            },
        ]
    )

    kpis = calculate_kpis(df)
    assert kpis["total_orders"] == 3
    assert kpis["completed_orders"] == 2
    assert kpis["cancelled_orders"] == 1
    assert kpis["late_deliveries"] == 1
    assert kpis["late_delivery_rate"] == 0.5
    assert kpis["estimated_value_of_cancelled_orders"] == 35


def test_calculate_kpis_handles_empty_dataframe():
    kpis = calculate_kpis(pd.DataFrame())
    assert kpis["total_orders"] == 0
    assert kpis["late_delivery_rate"] == 0.0
    assert kpis["estimated_gross_order_value"] == 0.0
