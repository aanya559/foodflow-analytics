from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_food_delivery_data(n_orders: int = 15000, seed: int = 42) -> pd.DataFrame:
    """Generate a reproducible synthetic food delivery dataset."""
    rng = np.random.default_rng(seed)
    restaurant_names = {
        1: "Green Bowl",
        2: "Saffron Hub",
        3: "North Street Pizza",
        4: "Curry Crest",
        5: "Wild Leaf",
        6: "Harbor Bites",
        7: "Market Grill",
        8: "Sunset Sushi",
        9: "Bamboo Wok",
        10: "Meadow Deli",
        11: "City Tacos",
        12: "Oak & Onion",
        13: "Bistro 3",
        14: "Velvet Burger",
        15: "Tandoori Lane",
        16: "Roundabout Pasta",
        17: "Luna Cafe",
        18: "Riverside BBQ",
        19: "Delta Pies",
        20: "Prime Noodles",
    }
    zones = ["Downtown", "Uptown", "Riverside", "Old Town", "Harbor", "Midtown"]
    weather_options = ["Clear", "Cloudy", "Rain", "Storm", "Fog"]
    traffic_options = ["Low", "Moderate", "High", "Severe"]
    status_options = ["Completed", "Cancelled"]

    restaurant_ids = rng.integers(1, 21, size=n_orders)
    zone_ids = rng.choice(zones, size=n_orders)
    weather = rng.choice(weather_options, size=n_orders, p=[0.35, 0.25, 0.2, 0.1, 0.1])
    traffic = rng.choice(traffic_options, size=n_orders, p=[0.32, 0.3, 0.24, 0.14])
    order_values = np.clip(rng.normal(28, 12, size=n_orders), 6, 120)
    discounts = np.clip(rng.normal(3.5, 2.5, size=n_orders), 0, 20)

    start_date = pd.Timestamp("2024-01-01")
    end_date = pd.Timestamp("2024-12-31")
    date_offsets = rng.integers(0, (end_date - start_date).days + 1, size=n_orders)
    order_dates = start_date + pd.to_timedelta(date_offsets, unit="D")

    order_times = pd.to_datetime(
        rng.integers(0, 24 * 60, size=n_orders), unit="m"
    ).strftime("%H:%M")

    order_distance = np.clip(rng.lognormal(mean=1.4, sigma=0.65, size=n_orders), 1.0, 25.0)

    workload = np.array([0.5 + (i % 7) * 0.08 for i in range(n_orders)])
    prep_times = (
        12
        + 0.9 * order_distance
        + 5 * np.where(traffic == "Moderate", 1, 0)
        + 8 * np.where(traffic == "High", 1, 0)
        + 12 * np.where(traffic == "Severe", 1, 0)
        + 5 * np.where(weather == "Rain", 1, 0)
        + 8 * np.where(weather == "Storm", 1, 0)
        + 9 * np.where(weather == "Fog", 1, 0)
        + workload * 6
        + rng.normal(0, 4, size=n_orders)
    )
    prep_times = np.clip(prep_times, 6, 140).round(1)

    base_estimated = 18 + 1.8 * order_distance + 5 * np.where(traffic == "Moderate", 1, 0) + 10 * np.where(traffic == "High", 1, 0) + 15 * np.where(traffic == "Severe", 1, 0)
    base_estimated += 4 * np.where(weather == "Rain", 1, 0) + 8 * np.where(weather == "Storm", 1, 0) + 6 * np.where(weather == "Fog", 1, 0)
    estimated_delivery = np.clip(base_estimated + rng.normal(0, 4, size=n_orders), 8, 120).round(1)

    cancellation_prob = (
        0.03
        + 0.05 * np.where(traffic == "Moderate", 1, 0)
        + 0.10 * np.where(traffic == "High", 1, 0)
        + 0.16 * np.where(traffic == "Severe", 1, 0)
        + 0.06 * np.where(weather == "Rain", 1, 0)
        + 0.10 * np.where(weather == "Storm", 1, 0)
        + 0.08 * np.where(weather == "Fog", 1, 0)
        + 0.04 * np.where(prep_times > 45, 1, 0)
    )
    cancellation_mask = rng.random(n_orders) < cancellation_prob

    order_status = np.where(cancellation_mask, "Cancelled", "Completed")
    cancellation_reasons = np.full(n_orders, np.nan, dtype=object)
    reason_map = {
        0: "High traffic delay",
        1: "Restaurant preparation delay",
        2: "Customer request",
        3: "Payment issue",
        4: "Delivery partner unavailable",
        5: "Weather conditions",
    }
    cancellation_indices = np.where(cancellation_mask)[0]
    cancellation_reasons[cancellation_indices] = np.array(
        [reason_map[int(i % len(reason_map))] for i in cancellation_indices],
        dtype=object,
    )

    actual_delivery = np.full(n_orders, np.nan, dtype=float)
    completed_mask = order_status == "Completed"
    actual_delivery[completed_mask] = (
        estimated_delivery[completed_mask]
        + 0.8 * (1 + np.where(traffic[completed_mask] == "Moderate", 1, 0))
        + 4 * np.where(traffic[completed_mask] == "High", 1, 0)
        + 8 * np.where(traffic[completed_mask] == "Severe", 1, 0)
        + 3 * np.where(weather[completed_mask] == "Rain", 1, 0)
        + 7 * np.where(weather[completed_mask] == "Storm", 1, 0)
        + 5 * np.where(weather[completed_mask] == "Fog", 1, 0)
        + 1.5 * order_distance[completed_mask]
        + rng.normal(0, 5, size=np.sum(completed_mask))
    )
    actual_delivery = np.clip(actual_delivery, 5, 170).round(1)

    customer_ratings = np.full(n_orders, np.nan, dtype=float)
    customer_ratings[completed_mask] = np.clip(
        rng.normal(4.45, 0.38, size=np.sum(completed_mask)), 2.5, 5.0
    )
    partner_ids = rng.integers(100, 250, size=n_orders)

    restaurant_names_column = [restaurant_names[int(i)] for i in restaurant_ids]
    data = pd.DataFrame(
        {
            "order_id": [f"FD-{idx:06d}" for idx in range(1, n_orders + 1)],
            "order_date": order_dates,
            "order_time": order_times,
            "restaurant_id": restaurant_ids,
            "restaurant_name": restaurant_names_column,
            "delivery_zone": zone_ids,
            "order_value": np.round(order_values, 2),
            "preparation_time_minutes": np.round(prep_times, 1),
            "estimated_delivery_minutes": np.round(estimated_delivery, 1),
            "actual_delivery_minutes": np.round(actual_delivery, 1),
            "delivery_distance_km": np.round(order_distance, 2),
            "weather_condition": weather,
            "traffic_level": traffic,
            "order_status": order_status,
            "cancellation_reason": cancellation_reasons,
            "delivery_partner_id": partner_ids,
            "customer_rating": np.round(customer_ratings, 2),
            "discount_amount": np.round(np.clip(discounts, 0, 15), 2),
        }
    )

    data["order_date"] = pd.to_datetime(data["order_date"]).dt.date
    data["order_date"] = pd.to_datetime(data["order_date"])
    return data


def save_synthetic_dataset(path: str | Path, n_orders: int = 15000, seed: int = 42) -> pd.DataFrame:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_food_delivery_data(n_orders=n_orders, seed=seed)
    df.to_csv(output_path, index=False)
    return df
