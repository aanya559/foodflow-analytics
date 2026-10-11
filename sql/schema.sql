PRAGMA foreign_keys = OFF;

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
);

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_zone ON orders(delivery_zone);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant ON orders(restaurant_name);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_traffic ON orders(traffic_level);
CREATE INDEX IF NOT EXISTS idx_orders_weather ON orders(weather_condition);
