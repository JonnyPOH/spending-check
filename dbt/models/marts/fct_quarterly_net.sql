select
    {{ year_quarter_period('transaction_date') }}  as period,
    round(sum(amount), 2)                          as net_amount
from {{ ref('stg_transactions') }}
group by {{ year_quarter_period('transaction_date') }}
order by period
