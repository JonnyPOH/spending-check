{# Format a date column as YYYY-MM #}
{% macro date_to_period(col) %}
  {% if target.type == 'bigquery' %}
    FORMAT_DATE('%Y-%m', {{ col }})
  {% else %}
    strftime({{ col }}, '%Y-%m')
  {% endif %}
{% endmacro %}

{# Format a date column as YY-Q (e.g. 25-1) #}
{% macro year_quarter_period(col) %}
  {% if target.type == 'bigquery' %}
    CONCAT(
      SUBSTR(CAST(EXTRACT(YEAR FROM {{ col }}) AS STRING), 3, 2),
      '-',
      CAST(EXTRACT(QUARTER FROM {{ col }}) AS STRING)
    )
  {% else %}
    SUBSTR(CAST(year({{ col }}) AS VARCHAR), 3, 2)
    || '-' || CAST(quarter({{ col }}) AS VARCHAR)
  {% endif %}
{% endmacro %}

{# First day of the month N months ago from today #}
{% macro months_ago(n) %}
  {% if target.type == 'bigquery' %}
    DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL {{ n }} MONTH)
  {% else %}
    date_trunc('month', current_date) - INTERVAL '{{ n }} months'
  {% endif %}
{% endmacro %}

{# Extract year from a date #}
{% macro extract_year(col) %}
  {% if target.type == 'bigquery' %}
    EXTRACT(YEAR FROM {{ col }})
  {% else %}
    year({{ col }})
  {% endif %}
{% endmacro %}

{# Extract month from a date #}
{% macro extract_month(col) %}
  {% if target.type == 'bigquery' %}
    EXTRACT(MONTH FROM {{ col }})
  {% else %}
    month({{ col }})
  {% endif %}
{% endmacro %}

{# Months elapsed between two date columns #}
{% macro date_diff_months(start_col, end_col) %}
  {% if target.type == 'bigquery' %}
    DATE_DIFF({{ end_col }}, {{ start_col }}, MONTH)
  {% else %}
    datediff('month', {{ start_col }}, {{ end_col }})
  {% endif %}
{% endmacro %}

{# Cast a column to string (VARCHAR / STRING) #}
{% macro cast_string(col) %}
  {% if target.type == 'bigquery' %}
    CAST({{ col }} AS STRING)
  {% else %}
    CAST({{ col }} AS VARCHAR)
  {% endif %}
{% endmacro %}
