with merchant_months as (
    select
        merchant,
        {{ date_to_period('transaction_date') }}  as year_month,
        max(transaction_date)                     as last_seen
    from {{ ref('stg_transactions') }}
    where
        amount < 0
        and merchant is not null
        and transaction_date >= {{ months_ago(var('dormant_lookback_months')) }}
    group by merchant, {{ date_to_period('transaction_date') }}
),

summary as (
    select
        merchant,
        count(distinct year_month)                                    as months_active,
        max(last_seen)                                                as last_transaction_date,
        {{ date_diff_months('max(last_seen)', 'current_date') }}      as months_since_last
    from merchant_months
    group by merchant
)

select
    merchant,
    months_active,
    last_transaction_date,
    months_since_last
from summary
where
    months_active >= 2
    and months_since_last >= {{ var('dormant_gap_months') }}
order by months_since_last desc
