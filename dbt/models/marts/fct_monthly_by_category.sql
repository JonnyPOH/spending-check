select
    category,
    sum(abs(amount))  as total_spend,
    count(*)          as transaction_count,
    avg(abs(amount))  as avg_transaction
from {{ ref('stg_transactions') }}
where
    amount < 0
    and {{ extract_year('transaction_date') }}  = {{ var('target_year') }}
    and {{ extract_month('transaction_date') }} = {{ var('target_month') }}
group by category
order by total_spend desc
