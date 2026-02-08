WITH customer_metrics AS (
    SELECT 
        customer_id,
        MAX(invoice_date) as last_purchase_date,
        MIN(invoice_date) as first_purchase_date,
        COUNT(DISTINCT invoice_no) as frequency,
        SUM(total_amount) as monetary,
        AVG(total_amount) as avg_order_value
    FROM online_retail
    WHERE quantity > 0 
      AND unit_price > 0
      AND customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'  -- Exclude cancellations
    GROUP BY customer_id
),
rfm_calc AS (
    SELECT 
        customer_id,
        frequency,
        monetary,
        avg_order_value,
        DATEDIFF(day, last_purchase_date, '2011-12-10') as recency,
        DATEDIFF(day, first_purchase_date, last_purchase_date) as customer_lifespan_days
    FROM customer_metrics
)
SELECT 
    customer_id,
    recency,
    frequency,
    monetary,
    avg_order_value,
    customer_lifespan_days,
    -- RFM Scores (1-5 scale using quintiles)
    NTILE(5) OVER (ORDER BY recency DESC) as r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) as m_score
FROM rfm_calc;