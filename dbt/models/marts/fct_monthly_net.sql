select
    {{ date_to_period('transaction_date') }}  as period,
    round(sum(amount), 2)                     as net_amount
from {{ ref('stg_transactions') }}
group by {{ date_to_period('transaction_date') }}
order by period
