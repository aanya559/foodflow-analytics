-- 1) Overall operational KPIs
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN order_status = 'Completed' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    AVG(CASE WHEN order_status = 'Completed' THEN actual_delivery_minutes END) AS avg_actual_delivery_time,
    AVG(preparation_time_minutes) AS avg_preparation_time,
    AVG(delivery_distance_km) AS avg_distance_km,
    AVG(order_value) AS avg_order_value
FROM orders;

-- 2) Daily trends
SELECT
    order_date,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    SUM(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1 ELSE 0 END) AS late_orders
FROM orders
GROUP BY order_date
ORDER BY order_date;

-- 3) Restaurant performance
WITH completed AS (
    SELECT restaurant_name,
           COUNT(*) AS total_orders,
           AVG(preparation_time_minutes) AS avg_prep_minutes,
           AVG(CASE WHEN actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY restaurant_name
)
SELECT *
FROM completed
WHERE total_orders >= 10
ORDER BY late_rate DESC;

-- 4) Zone performance
SELECT
    delivery_zone,
    COUNT(*) AS total_orders,
    AVG(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate,
    AVG(CASE WHEN order_status = 'Completed' THEN actual_delivery_minutes END) AS avg_delivery_minutes
FROM orders
GROUP BY delivery_zone
HAVING COUNT(*) >= 15
ORDER BY late_rate DESC;

-- 5) Late deliveries by hour of day
SELECT
    CAST(substr(order_time, 1, 2) AS INTEGER) AS hour_of_day,
    AVG(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate,
    COUNT(*) AS total_orders
FROM orders
GROUP BY CAST(substr(order_time, 1, 2) AS INTEGER)
ORDER BY hour_of_day;

-- 6) Preparation vs delivery time
SELECT
    restaurant_name,
    AVG(preparation_time_minutes) AS avg_prep_minutes,
    AVG(actual_delivery_minutes) AS avg_delivery_minutes
FROM orders
WHERE order_status = 'Completed'
GROUP BY restaurant_name
ORDER BY avg_prep_minutes DESC;

-- 7) Traffic and weather comparisons
SELECT
    traffic_level,
    weather_condition,
    COUNT(*) AS total_orders,
    AVG(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate
FROM orders
GROUP BY traffic_level, weather_condition
ORDER BY late_rate DESC;

-- 8) Cancellation reasons
SELECT
    cancellation_reason,
    COUNT(*) AS cancelled_orders,
    AVG(CASE WHEN order_status = 'Cancelled' THEN 1.0 ELSE 0.0 END) AS cancellation_rate
FROM orders
WHERE order_status = 'Cancelled'
GROUP BY cancellation_reason
ORDER BY cancelled_orders DESC;

-- 9) Delivery partner performance
SELECT
    delivery_partner_id,
    COUNT(*) AS completed_deliveries,
    AVG(customer_rating) AS avg_customer_rating,
    AVG(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate
FROM orders
WHERE order_status = 'Completed'
GROUP BY delivery_partner_id
HAVING COUNT(*) >= 20
ORDER BY late_rate DESC;

-- 10) Customer rating patterns
SELECT
    CASE
        WHEN customer_rating >= 4.5 THEN 'Excellent'
        WHEN customer_rating >= 4.0 THEN 'Good'
        WHEN customer_rating >= 3.5 THEN 'Fair'
        ELSE 'Low'
    END AS rating_band,
    COUNT(*) AS ratings,
    AVG(actual_delivery_minutes) AS avg_delivery_minutes
FROM orders
WHERE order_status = 'Completed'
GROUP BY rating_band
ORDER BY ratings DESC;

-- 11) Order value by outcome
SELECT
    order_status,
    AVG(order_value) AS avg_order_value,
    SUM(order_value) AS total_value,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status;

-- 12) Poor performing segments
SELECT
    delivery_zone,
    restaurant_name,
    AVG(CASE WHEN order_status = 'Completed' AND actual_delivery_minutes > estimated_delivery_minutes THEN 1.0 ELSE 0.0 END) AS late_rate,
    COUNT(*) AS order_count
FROM orders
GROUP BY delivery_zone, restaurant_name
HAVING COUNT(*) >= 10
ORDER BY late_rate DESC;
