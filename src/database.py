from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def create_database_schema(db_path: str | Path) -> Path:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                order_date TEXT,
                order_time TEXT,
                restaurant_id INTEGER,
                restaurant_name TEXT,
                delivery_zone TEXT,
                order_value REAL,
                preparation_time_minutes REAL,
                estimated_delivery_minutes REAL,
                actual_delivery_minutes REAL,
                delivery_distance_km REAL,
                weather_condition TEXT,
                traffic_level TEXT,
                order_status TEXT,
                cancellation_reason TEXT,
                delivery_partner_id INTEGER,
                customer_rating REAL,
                discount_amount REAL
            )
            """
        )
    return db_file


def populate_database(db_path: str | Path, df: pd.DataFrame) -> Path:
    db_file = create_database_schema(db_path)
    with sqlite3.connect(db_file) as conn:
        conn.execute("DELETE FROM orders")
        rows = [
            (
                row["order_id"],
                row["order_date"].strftime("%Y-%m-%d") if pd.notna(row["order_date"]) else None,
                row["order_time"],
                row["restaurant_id"],
                row["restaurant_name"],
                row["delivery_zone"],
                row["order_value"],
                row["preparation_time_minutes"],
                row["estimated_delivery_minutes"],
                row["actual_delivery_minutes"],
                row["delivery_distance_km"],
                row["weather_condition"],
                row["traffic_level"],
                row["order_status"],
                row["cancellation_reason"],
                row["delivery_partner_id"],
                row["customer_rating"],
                row["discount_amount"],
            )
            for _, row in df.iterrows()
        ]
        conn.executemany(
            """
            INSERT INTO orders (
                order_id, order_date, order_time, restaurant_id, restaurant_name,
                delivery_zone, order_value, preparation_time_minutes,
                estimated_delivery_minutes, actual_delivery_minutes,
                delivery_distance_km, weather_condition, traffic_level, order_status,
                cancellation_reason, delivery_partner_id, customer_rating, discount_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    return db_file
