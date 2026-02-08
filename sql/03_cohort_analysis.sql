WITH user_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date)) as cohort_month
    FROM online_retail
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT 
        r.customer_id,
        u.cohort_month,
        DATE_TRUNC('month', r.invoice_date) as activity_month,
        COUNT(DISTINCT r.invoice_no) as orders
    FROM online_retail r
    JOIN user_cohorts u ON r.customer_id = u.customer_id
    WHERE r.customer_id IS NOT NULL
    GROUP BY r.customer_id, u.cohort_month, DATE_TRUNC('month', r.invoice_date)
)
SELECT 
    cohort_month,
    PERIOD_DIFF(EXTRACT(YEAR_MONTH FROM activity_month), 
                EXTRACT(YEAR_MONTH FROM cohort_month)) as periods_since_first,
    COUNT(DISTINCT customer_id) as active_customers,
    ROUND(COUNT(DISTINCT customer_id) * 100.0 / 
          FIRST_VALUE(COUNT(DISTINCT customer_id)) OVER (
              PARTITION BY cohort_month 
              ORDER BY periods_since_first
          ), 2) as retention_rate
FROM activity
GROUP BY cohort_month, periods_since_first
ORDER BY cohort_month, periods_since_first;