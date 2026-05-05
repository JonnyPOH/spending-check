-- Month-over-month spend per category for the last N months.
-- Params: :months INT (default 6)
-- Returns one row per (year_month, category).

WITH monthly AS (
    SELECT
        strftime(transaction_date, '%Y-%m') AS year_month,
        category,
        SUM(ABS(amount))                    AS total_spend
    FROM transactions
    WHERE
        amount < 0
        AND transaction_date >= date_trunc('month', current_date) - INTERVAL ':months months'
    GROUP BY strftime(transaction_date, '%Y-%m'), category
)
SELECT
    year_month,
    category,
    total_spend,
    LAG(total_spend) OVER (PARTITION BY category ORDER BY year_month) AS prev_month_spend,
    ROUND(
        100.0 * (total_spend - LAG(total_spend) OVER (PARTITION BY category ORDER BY year_month))
             / NULLIF(LAG(total_spend) OVER (PARTITION BY category ORDER BY year_month), 0),
        1
    ) AS pct_change
FROM monthly
ORDER BY category, year_month;
