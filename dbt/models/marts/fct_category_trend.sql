with monthly as (
    select
        {{ date_to_period('transaction_date') }}  as year_month,
        category,
        sum(abs(amount))                          as total_spend
    from {{ ref('stg_transactions') }}
    where
        amount < 0
        and transaction_date >= {{ months_ago(var('category_trend_months')) }}
    group by {{ date_to_period('transaction_date') }}, category
)

select
    year_month,
    category,
    total_spend,
    lag(total_spend) over (partition by category order by year_month)  as prev_month_spend,
    round(
        100.0 * (
            total_spend
            - lag(total_spend) over (partition by category order by year_month)
        ) / nullif(
            lag(total_spend) over (partition by category order by year_month), 0
        ),
        1
    )                                                                  as pct_change
from monthly
order by category, year_month
