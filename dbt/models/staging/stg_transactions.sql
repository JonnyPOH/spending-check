with source as (
    select * from {{ source('raw', 'transactions') }}
)

select
    transaction_date,
    trim(description)                                                                    as description,
    amount,
    lower(trim(category))                                                                as category,
    lower(trim(coalesce(nullif(broad, ''), category)))                                   as broad,
    coalesce(nullif(trim({{ cast_string('merchant') }}), ''), null)                      as merchant,
    currency
from source
where transaction_date is not null
  and amount is not null
