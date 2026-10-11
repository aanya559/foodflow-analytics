from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from .database import populate_database
from .data_generator import generate_food_delivery_data

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "foodflow.db"
CSV_PATH = DATA_DIR / "foodflow_orders.csv"


def ensure_project_data() -> tuple[Path, Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        df = generate_food_delivery_data()
        df.to_csv(CSV_PATH, index=False)
    if not DB_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        populate_database(DB_PATH, df)
    return CSV_PATH, DB_PATH


def load_orders_data(db_path: str | Path = DB_PATH) -> pd.DataFrame:
    db_file = Path(db_path)
    if not db_file.exists():
        ensure_project_data()
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql_query("SELECT * FROM orders", conn)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    filtered = df.copy()
    if filters.get("start_date"):
        filtered = filtered[filtered["order_date"] >= pd.to_datetime(filters["start_date"])]
    if filters.get("end_date"):
        filtered = filtered[filtered["order_date"] <= pd.to_datetime(filters["end_date"])]
    if filters.get("zone"):
        filtered = filtered[filtered["delivery_zone"].isin(filters["zone"])]
    if filters.get("restaurant"):
        filtered = filtered[filtered["restaurant_name"].isin(filters["restaurant"])]
    if filters.get("traffic_level"):
        filtered = filtered[filtered["traffic_level"].isin(filters["traffic_level"])]
    if filters.get("weather_condition"):
        filtered = filtered[filtered["weather_condition"].isin(filters["weather_condition"])]
    if filters.get("order_status"):
        filtered = filtered[filtered["order_status"].isin(filters["order_status"])]
    return filtered


def get_filter_options(df: pd.DataFrame) -> dict[str, list[str]]:
    return {
        "zones": sorted(df["delivery_zone"].dropna().unique().tolist()),
        "restaurants": sorted(df["restaurant_name"].dropna().unique().tolist()),
        "traffic_levels": sorted(df["traffic_level"].dropna().unique().tolist()),
        "weather_conditions": sorted(df["weather_condition"].dropna().unique().tolist()),
        "order_status": sorted(df["order_status"].dropna().unique().tolist()),
    }
