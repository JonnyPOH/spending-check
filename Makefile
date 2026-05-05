.PHONY: pipeline app serve test lint

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
