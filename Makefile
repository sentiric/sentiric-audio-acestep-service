.PHONY: setup clean dev-up dev-down dev-logs

VENV = .venv
UV = uv

setup:
	@echo "🚀 Setting up virtual environment..."
	$(UV) venv $(VENV)
	$(UV) pip install -r requirements.txt

clean:
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

# --- LOCAL DEV ENVIRONMENT ---
dev-up:
	@echo "🔥 Starting ACE-Step (MusicGen) environment..."
	docker compose up --build -d

dev-logs:
	@echo "📋 Tailing logs..."
	docker compose logs -f audio-acestep-service

dev-down:
	@echo "🛑 Shutting down environment..."
	docker compose down -v

# Mevcut komutların altına ekleyin
setup-test:
	uv venv
	uv pip install grpcio 
	uv pip install sentiric-contracts-py git+https://github.com/sentiric/sentiric-contracts.git@v1.25.0

test:
	@echo "🧪 Running ACE-Step Music Test..."
	$(VENV)/bin/python test_client.py --category all