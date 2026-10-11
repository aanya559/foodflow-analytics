from __future__ import annotations

import pandas as pd

from src.data_validation import validate_orders, clean_duplicate_orders


def test_validate_orders_detects_missing_duplicates_and_invalid_values():
    df = pd.DataFrame(
        [
            {
                "order_id": "FD-001",
                "order_status": "Completed",
                "actual_delivery_minutes": 35,
                "estimated_delivery_minutes": 30,
                "preparation_time_minutes": 12,
                "delivery_distance_km": 4,
                "order_value": 20,
                "customer_rating": 4.7,
                "cancellation_reason": None,
            },
            {
                "order_id": "FD-001",
                "order_status": "Completed",
                "actual_delivery_minutes": 35,
                "estimated_delivery_minutes": 30,
                "preparation_time_minutes": 12,
                "delivery_distance_km": 4,
                "order_value": 20,
                "customer_rating": 4.7,
                "cancellation_reason": None,
            },
            {
                "order_id": "FD-002",
                "order_status": "Cancelled",
                "actual_delivery_minutes": None,
                "estimated_delivery_minutes": 30,
                "preparation_time_minutes": 0,
                "delivery_distance_km": 0,
                "order_value": -1,
                "customer_rating": None,
                "cancellation_reason": "",
            },
        ]
    )

    summary = validate_orders(df)
    assert summary["duplicate_rows"] == 1
    assert summary["invalid_durations"] >= 1
    assert summary["inconsistent_statuses"] >= 1


def test_clean_duplicate_orders_keeps_first_unique_record():
    df = pd.DataFrame(
        [
            {"order_id": "FD-001", "order_status": "Completed", "order_value": 20},
            {"order_id": "FD-001", "order_status": "Completed", "order_value": 25},
            {"order_id": "FD-002", "order_status": "Cancelled", "order_value": 15},
        ]
    )
    cleaned = clean_duplicate_orders(df)
    assert len(cleaned) == 2
    assert cleaned.loc[cleaned["order_id"] == "FD-001", "order_value"].iloc[0] == 20
