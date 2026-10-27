run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest

lint:
	ruff check .

samples:
	python scripts/generate_samples.py
