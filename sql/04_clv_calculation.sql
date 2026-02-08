WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT invoice_no) as total_orders,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value,
        MIN(invoice_date) as first_order,
        MAX(invoice_date) as last_order,
        DATEDIFF(day, MIN(invoice_date), MAX(invoice_date)) / 30.0 as lifespan_months
    FROM online_retail
    WHERE quantity > 0 AND unit_price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
    HAVING COUNT(DISTINCT invoice_no) > 1  -- Repeat customers only
)
SELECT 
    customer_id,
    total_orders,
    total_revenue,
    avg_order_value,
    lifespan_months,
    CASE 
        WHEN lifespan_months > 0 THEN total_orders / lifespan_months 
        ELSE 0 
    END as purchase_frequency_monthly,
    -- CLV Formula: AOV × Purchase Frequency × Lifespan
    avg_order_value * 
    CASE WHEN lifespan_months > 0 THEN total_orders / lifespan_months ELSE 0 END * 
    lifespan_months as estimated_clv
FROM customer_stats
ORDER BY estimated_clv DESC;