.PHONY: install lint format typecheck test run docker-build docker-run clean

install:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

lint:
	ruff check .
	black --check .

format:
	black .

typecheck:
	mypy backend

test:
	pytest

run:
	uvicorn backend.main:app --reload

docker-build:
	docker build -t dfs-app .

docker-run:
	docker run -p 8000:8000 dfs-app

clean:
	rm -rf logs/*.pdf __pycache__ .mypy_cache .ruff_cache .pytest_cache
