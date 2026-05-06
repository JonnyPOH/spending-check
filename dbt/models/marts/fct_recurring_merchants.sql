with monthly_merchant as (
    select
        merchant,
        strftime(transaction_date, '%Y-%m')  as year_month,
        sum(abs(amount))                     as monthly_spend
    from {{ ref('stg_transactions') }}
    where
        amount < 0
        and merchant is not null
        and transaction_date >= date_trunc('month', current_date)
            - interval '{{ var("recurring_lookback_months") }} months'
    group by merchant, strftime(transaction_date, '%Y-%m')
),

stats as (
    select
        merchant,
        count(distinct year_month)  as months_active,
        avg(monthly_spend)          as avg_monthly_spend,
        stddev(monthly_spend)       as stdev_spend
    from monthly_merchant
    group by merchant
)

select
    merchant,
    months_active,
    round(avg_monthly_spend, 2)  as avg_monthly_spend,
    round(stdev_spend, 2)        as stdev_spend,
    round(
        case when avg_monthly_spend > 0
             then stdev_spend / avg_monthly_spend
             else null
        end,
        3
    )                            as coefficient_of_variation
from stats
where months_active >= {{ var('recurring_min_months') }}
order by avg_monthly_spend desc
