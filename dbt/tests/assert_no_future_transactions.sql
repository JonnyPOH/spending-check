-- Fails if any transactions are dated in the future
select transaction_date
from {{ ref('stg_transactions') }}
where transaction_date > current_date
