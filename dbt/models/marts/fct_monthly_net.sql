select
    strftime(transaction_date, '%Y-%m')  as period,
    round(sum(amount), 2)                as net_amount
from {{ ref('stg_transactions') }}
group by period
order by period
