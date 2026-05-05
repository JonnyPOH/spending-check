-- Merchants that appear on a near-monthly cadence (likely subscriptions).
-- Params: :min_months INT (default 3), :lookback_months INT (default 6)

WITH monthly_merchant AS (
    SELECT
        merchant,
        strftime(transaction_date, '%Y-%m') AS year_month,
        SUM(ABS(amount))                    AS monthly_spend
    FROM transactions
    WHERE
        amount < 0
        AND merchant IS NOT NULL
        AND transaction_date >= date_trunc('month', current_date) - INTERVAL ':lookback_months months'
    GROUP BY merchant, strftime(transaction_date, '%Y-%m')
),
stats AS (
    SELECT
        merchant,
        COUNT(DISTINCT year_month)  AS months_active,
        AVG(monthly_spend)          AS avg_monthly_spend,
        stddev(monthly_spend)       AS stdev_spend
    FROM monthly_merchant
    GROUP BY merchant
)
SELECT
    merchant,
    months_active,
    ROUND(avg_monthly_spend, 2)  AS avg_monthly_spend,
    ROUND(stdev_spend, 2)        AS stdev_spend,
    ROUND(
        CASE WHEN avg_monthly_spend > 0
             THEN stdev_spend / avg_monthly_spend
             ELSE NULL
        END, 3
    )                            AS coefficient_of_variation
FROM stats
WHERE months_active >= :min_months
ORDER BY avg_monthly_spend DESC;
