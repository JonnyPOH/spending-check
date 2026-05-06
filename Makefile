.PHONY: pipeline app serve test lint dbt-load dbt dbt-test dbt-docs

pipeline:
	python -m src.pipeline

app:
	streamlit run app.py

serve:
	uvicorn api:app --reload --port 8001

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# dbt targets — run from spending_check/ directory
dbt-load:
	python dbt/load_source.py

dbt: dbt-load
	dbt run --project-dir dbt --profiles-dir dbt

dbt-test: dbt
	dbt test --project-dir dbt --profiles-dir dbt

dbt-docs: dbt
	dbt docs generate --project-dir dbt --profiles-dir dbt
	dbt docs serve --project-dir dbt --profiles-dir dbt
