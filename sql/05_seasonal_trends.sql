-- Monthly revenue trends with YoY comparison
WITH monthly_stats AS (
    SELECT 
        EXTRACT(YEAR FROM invoice_date) as year,
        EXTRACT(MONTH FROM invoice_date) as month,
        SUM(total_amount) as revenue,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT invoice_no) as total_orders
    FROM online_retail
    WHERE invoice_no NOT LIKE 'C%'
    GROUP BY EXTRACT(YEAR FROM invoice_date), EXTRACT(MONTH FROM invoice_date)
)
SELECT 
    month,
    year,
    revenue,
    unique_customers,
    total_orders,
    LAG(revenue) OVER (PARTITION BY month ORDER BY year) as prev_year_revenue,
    ROUND((revenue - LAG(revenue) OVER (PARTITION BY month ORDER BY year)) * 100.0 / 
          LAG(revenue) OVER (PARTITION BY month ORDER BY year), 2) as yoy_growth_pct
FROM monthly_stats
ORDER BY year, month;