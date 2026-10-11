from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_generator import save_synthetic_dataset
from src.database import populate_database


def initialize_project_data() -> tuple[Path, Path]:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    csv_path = data_dir / "foodflow_orders.csv"
    db_path = data_dir / "foodflow.db"
    data_dir.mkdir(parents=True, exist_ok=True)

    df = save_synthetic_dataset(csv_path, n_orders=15000, seed=42)
    populate_database(db_path, df)
    return csv_path, db_path


if __name__ == "__main__":
    initialize_project_data()
    print("Initialized synthetic dataset and SQLite database.")
