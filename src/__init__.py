"""FoodFlow Analytics core package."""

from .data_generator import generate_food_delivery_data
from .data_validation import validate_orders, clean_duplicate_orders
from .kpi_calculations import calculate_kpis, late_delivery_flag
from .analytics import (
    get_daily_order_trends,
    get_restaurant_performance,
    get_zone_performance,
    get_cancellation_summary,
)

__all__ = [
    "generate_food_delivery_data",
    "validate_orders",
    "clean_duplicate_orders",
    "calculate_kpis",
    "late_delivery_flag",
    "get_daily_order_trends",
    "get_restaurant_performance",
    "get_zone_performance",
    "get_cancellation_summary",
]
