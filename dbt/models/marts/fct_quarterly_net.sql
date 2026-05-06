select
    substr(cast(year(transaction_date) as varchar), 3, 2)
        || '-' || cast(quarter(transaction_date) as varchar)  as period,
    round(sum(amount), 2)                                      as net_amount
from {{ ref('stg_transactions') }}
group by period
order by period
