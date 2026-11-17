-- ============================================================
-- Pan-African E-Commerce Orders — Analysis Queries
-- Dialect: SQLite (standard ANSI SQL, portable to Postgres/MySQL/
-- Snowflake/BigQuery with minor date-function tweaks)
-- Table: orders (17,994 cleaned rows, Jan–Dec 2025)
-- ============================================================

-- 1. Revenue, orders and AOV by country -----------------------
SELECT
    country,
    COUNT(*)                           AS total_orders,
    ROUND(SUM(net_amount_usd), 2)      AS total_revenue_usd,
    ROUND(AVG(net_amount_usd), 2)      AS avg_order_value_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY country
ORDER BY total_revenue_usd DESC;


-- 2. Monthly revenue trend (overall) ---------------------------
SELECT
    order_month,
    COUNT(*)                       AS orders,
    ROUND(SUM(net_amount_usd), 2)  AS revenue_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY order_month
ORDER BY order_month;


-- 3. Top categories by revenue, with share of total ------------
WITH cat_rev AS (
    SELECT category, SUM(net_amount_usd) AS revenue
    FROM orders
    WHERE delivery_status != 'Cancelled'
    GROUP BY category
)
SELECT
    category,
    ROUND(revenue, 2) AS revenue_usd,
    ROUND(100.0 * revenue / (SELECT SUM(revenue) FROM cat_rev), 1) AS pct_of_total
FROM cat_rev
ORDER BY revenue DESC;


-- 4. Category mix by country (what sells where) ----------------
SELECT
    country,
    category,
    COUNT(*) AS orders,
    ROUND(SUM(net_amount_usd), 2) AS revenue_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY country, category
ORDER BY country, revenue_usd DESC;


-- 5. New vs returning customer contribution ---------------------
SELECT
    customer_segment,
    COUNT(*)                       AS orders,
    ROUND(SUM(net_amount_usd), 2)  AS revenue_usd,
    ROUND(AVG(net_amount_usd), 2)  AS avg_order_value_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY customer_segment;


-- 6. Repeat purchase rate (customers with 2+ orders) -------------
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                          AS total_customers,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)     AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_rate_pct
FROM order_counts;


-- 7. Delivery performance by country ------------------------------
SELECT
    country,
    COUNT(*)                                                       AS total_orders,
    ROUND(AVG(delivery_days), 1)                                   AS avg_delivery_days,
    ROUND(100.0 * SUM(CASE WHEN delivery_status = 'Delivered Late' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_late,
    ROUND(100.0 * SUM(CASE WHEN delivery_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1)       AS pct_cancelled,
    ROUND(100.0 * SUM(CASE WHEN delivery_status = 'Returned' THEN 1 ELSE 0 END) / COUNT(*), 1)        AS pct_returned
FROM orders
GROUP BY country
ORDER BY pct_cancelled DESC;


-- 8. Payment method mix and average basket size ------------------
SELECT
    payment_method,
    COUNT(*)                       AS orders,
    ROUND(AVG(net_amount_usd), 2)  AS avg_order_value_usd,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS pct_of_orders
FROM orders
GROUP BY payment_method
ORDER BY orders DESC;


-- 9. Discount impact: orders with vs without a discount ----------
SELECT
    CASE WHEN discount_pct > 0 THEN 'Discounted' ELSE 'Full Price' END AS order_type,
    COUNT(*)                           AS orders,
    ROUND(AVG(net_amount_usd), 2)      AS avg_order_value_usd,
    ROUND(AVG(quantity), 2)            AS avg_quantity
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY order_type;


-- 10. Customer satisfaction (rating) by country and delivery speed --
SELECT
    country,
    ROUND(AVG(customer_rating), 2) AS avg_rating,
    ROUND(AVG(delivery_days), 1)   AS avg_delivery_days,
    COUNT(customer_rating)         AS n_ratings
FROM orders
WHERE customer_rating IS NOT NULL
GROUP BY country
ORDER BY avg_rating DESC;


-- 11. Top 10 highest-revenue days (useful for ops/marketing retros) --
SELECT
    order_date,
    COUNT(*) AS orders,
    ROUND(SUM(net_amount_usd), 2) AS revenue_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY order_date
ORDER BY revenue_usd DESC
LIMIT 10;


-- 12. Weekend vs weekday order behavior ------------------------------
SELECT
    is_weekend,
    COUNT(*)                       AS orders,
    ROUND(AVG(net_amount_usd), 2)  AS avg_order_value_usd
FROM orders
WHERE delivery_status != 'Cancelled'
GROUP BY is_weekend;
