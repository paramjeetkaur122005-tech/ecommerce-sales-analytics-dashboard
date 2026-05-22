-- =====================================================
-- E-Commerce Sales Analytics SQL Queries
-- Dataset: Brazilian Olist E-Commerce Dataset
-- Purpose: Business analysis using SQL
-- =====================================================

-- 1. Monthly Revenue Trend
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
    ROUND(SUM(p.payment_value), 2) AS monthly_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
JOIN payments p 
    ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
ORDER BY order_month;


-- 2. Top 10 Product Categories by Revenue
SELECT
    pr.product_category_name,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS category_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM order_items oi
JOIN products pr 
    ON oi.product_id = pr.product_id
GROUP BY pr.product_category_name
ORDER BY category_revenue DESC
LIMIT 10;


-- 3. State-wise Orders and Revenue
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS total_customers,
    ROUND(SUM(p.payment_value), 2) AS total_revenue
FROM orders o
JOIN customers c 
    ON o.customer_id = c.customer_id
JOIN payments p 
    ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_orders DESC;


-- 4. Average Order Value by State
SELECT
    c.customer_state,
    ROUND(SUM(p.payment_value) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN customers c 
    ON o.customer_id = c.customer_id
JOIN payments p 
    ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY avg_order_value DESC;


-- 5. Delivery Performance: On-Time vs Late Orders
SELECT
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date 
        THEN 'Late'
        ELSE 'On Time'
    END AS delivery_status,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY delivery_status;


-- 6. Late Delivery Rate
SELECT
    ROUND(
        100.0 * SUM(
            CASE 
                WHEN order_delivered_customer_date > order_estimated_delivery_date 
                THEN 1 ELSE 0 
            END
        ) / COUNT(*),
        2
    ) AS late_delivery_rate_percentage
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;


-- 7. Top Customers by Total Spend
SELECT
    c.customer_unique_id,
    c.customer_state,
    ROUND(SUM(p.payment_value), 2) AS total_spent,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
JOIN customers c 
    ON o.customer_id = c.customer_id
JOIN payments p 
    ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id, c.customer_state
ORDER BY total_spent DESC
LIMIT 10;


-- 8. Payment Method Distribution
SELECT
    payment_type,
    COUNT(*) AS payment_count,
    ROUND(SUM(payment_value), 2) AS total_payment_value
FROM payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;