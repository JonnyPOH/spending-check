select
    broad,
    round(sum(amount), 2)                                                     as total_amount,
    round(
        sum(amount) / count(distinct strftime(transaction_date, '%Y-%m')),
        2
    )                                                                          as avg_per_month
from {{ ref('stg_transactions') }}
where broad is not null
  and broad != ''
group by broad
order by sum(amount) asc
