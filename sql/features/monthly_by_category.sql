-- Total spend per category for a given calendar month.
-- Params: :year INT, :month INT
-- Returns one row per category, ordered by spend descending.

SELECT
    category,
    SUM(ABS(amount))          AS total_spend,
    COUNT(*)                  AS transaction_count,
    AVG(ABS(amount))          AS avg_transaction
FROM transactions
WHERE
    amount < 0  -- debits only
    AND YEAR(transaction_date)  = :year
    AND MONTH(transaction_date) = :month
GROUP BY category
ORDER BY total_spend DESC;
