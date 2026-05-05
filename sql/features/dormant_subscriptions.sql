-- Merchants that were recurring but have gone quiet for >= :gap_months.
-- Params: :gap_months INT (default 2), :lookback_months INT (default 12)

WITH merchant_months AS (
    SELECT
        merchant,
        strftime(transaction_date, '%Y-%m')  AS year_month,
        MAX(transaction_date)                AS last_seen
    FROM transactions
    WHERE
        amount < 0
        AND merchant IS NOT NULL
        AND transaction_date >= date_trunc('month', current_date) - INTERVAL ':lookback_months months'
    GROUP BY merchant, strftime(transaction_date, '%Y-%m')
),
summary AS (
    SELECT
        merchant,
        COUNT(DISTINCT year_month)                      AS months_active,
        MAX(last_seen)                                  AS last_transaction_date,
        datediff('month', MAX(last_seen), current_date) AS months_since_last
    FROM merchant_months
    GROUP BY merchant
)
SELECT
    merchant,
    months_active,
    last_transaction_date,
    months_since_last
FROM summary
WHERE
    months_active >= 2
    AND months_since_last >= :gap_months
ORDER BY months_since_last DESC;
