with monthly as (
    select
        strftime(transaction_date, '%Y-%m')  as year_month,
        category,
        sum(abs(amount))                     as total_spend
    from {{ ref('stg_transactions') }}
    where
        amount < 0
        and transaction_date >= date_trunc('month', current_date)
            - interval '{{ var("category_trend_months") }} months'
    group by strftime(transaction_date, '%Y-%m'), category
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
