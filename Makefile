.PHONY: install generate-kb load-kb api dashboard docker-up docker-down clean

install:
	pip install -r requirements.txt

generate-kb:
	python -m src.knowledge.sample_kb

load-kb:
	python -m src.knowledge.kb_loader

api:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run src/dashboard/app.py --server.port 8501

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	rm -rf data/chroma_db __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
