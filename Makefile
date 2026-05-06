PYTHON := /home/jonnyoh/.pyenv/versions/3.12.4/bin/python3
DBT    := /home/jonnyoh/.pyenv/versions/3.12.4/bin/dbt

GCP_PROJECT := spending-check-495420
GCP_REGION  := europe-west2
SERVICE     := spending-check

.PHONY: pipeline app serve test lint deploy dbt-load dbt dbt-test dbt-docs

deploy:
	gcloud run deploy $(SERVICE) \
		--source . \
		--project $(GCP_PROJECT) \
		--region $(GCP_REGION) \
		--allow-unauthenticated

pipeline:
	$(PYTHON) -m src.pipeline

app:
	streamlit run app.py

serve:
	uvicorn api:app --reload --port 8001

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# dbt dev targets (DuckDB)
dbt-load:
	$(PYTHON) dbt/load_source.py

dbt: dbt-load
	$(DBT) run --project-dir dbt --profiles-dir dbt

dbt-test: dbt
	$(DBT) test --project-dir dbt --profiles-dir dbt

dbt-docs: dbt
	$(DBT) docs generate --project-dir dbt --profiles-dir dbt
	$(DBT) docs serve --project-dir dbt --profiles-dir dbt --port 8765 --no-browser

# dbt prod targets (BigQuery)
BQ_VARS := --vars '{"source_schema": "spending_check"}'

dbt-load-prod:
	$(PYTHON) dbt/load_source.py --target prod

dbt-prod: dbt-load-prod
	$(DBT) run --project-dir dbt --profiles-dir dbt --target prod $(BQ_VARS)

dbt-test-prod: dbt-prod
	$(DBT) test --project-dir dbt --profiles-dir dbt --target prod $(BQ_VARS)

dbt-docs-prod: dbt-prod
	$(DBT) docs generate --project-dir dbt --profiles-dir dbt --target prod $(BQ_VARS)
	$(DBT) docs serve --project-dir dbt --profiles-dir dbt --port 8765 --no-browser
