# ---------------------------------------------------------
# Makefile — Docker shortcuts for development
# ---------------------------------------------------------

# Default docker compose command
DC = docker compose

# ---------------------------------------------------------
# Chroma DB
# ---------------------------------------------------------
chroma:
	@echo "🚀 Starting Chroma..."
	$(DC) up -d --build chroma

chroma-nocache:
	@echo "🔥 Building Chroma with no cache..."
	$(DC) build --no-cache chroma
	$(DC) up -d chroma


# ---------------------------------------------------------
# Ingestion (LOCAL SCRIPT VERSION)
# ---------------------------------------------------------
# db_setup:
# 	@echo "📥 Running local ingestion..."
# 	@cd ingest && \
# 	python3 -m venv venv && \
# 	. venv/bin/activate && \
# 	pip install -r requirements.txt && \
# 	python setup_db.py && \
# 	deactivate && \
# 	cd ..
# 	@echo "🟢 Ingestion completed."

# ---------------------------------------------------------
# Backend
# ---------------------------------------------------------
backend:
	@echo "🚀 Starting backend..."
	$(DC) up -d --build backend

backend-nocache:
	@echo "🔥 Building backend with no cache..."
	$(DC) build --no-cache backend
	$(DC) up -d backend


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------
frontend:
	@echo "🚀 Starting frontend..."
	$(DC) up -d --build frontend

frontend-nocache:
	@echo "🔥 Building frontend with no cache..."
	$(DC) build --no-cache frontend
	$(DC) up -d frontend


# ---------------------------------------------------------
# Full stack
# ---------------------------------------------------------
up:
	$(DC) up -d --build

up-nocache:
	$(DC) build --no-cache
	$(DC) up -d


# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
down:
	@echo "🛑 Stopping all services..."
	$(DC) down

prune:
	@echo "🧹 Cleaning Docker system..."
	docker system prune -f
