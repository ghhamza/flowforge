# FlowForge — Developer commands
#
# Compose file layout:
#   docker-compose.yml            — infra (Postgres + Redis)
#   docker-compose.airflow.yml    — Airflow 3 stack
#   docker-compose.backend.yml    — FastAPI
#   docker-compose.frontend.yml   — Vite dev server
#
# "make up" boots everything. Individual targets let you run only what you need.

COMPOSE_INFRA   = docker compose -f docker-compose.yml
COMPOSE_AIRFLOW = docker compose -f docker-compose.yml -f docker-compose.airflow.yml
COMPOSE_BACKEND = docker compose -f docker-compose.yml -f docker-compose.backend.yml
COMPOSE_FRONT   = docker compose -f docker-compose.yml -f docker-compose.frontend.yml
COMPOSE_ALL     = docker compose -f docker-compose.yml -f docker-compose.airflow.yml -f docker-compose.backend.yml -f docker-compose.frontend.yml

# ── Full stack ───────────────────────────────────────────────
up:
	$(COMPOSE_ALL) up --build -d

down:
	$(COMPOSE_ALL) down

logs:
	$(COMPOSE_ALL) logs -f

restart:
	$(COMPOSE_ALL) down && $(COMPOSE_ALL) up --build -d

clean:
	$(COMPOSE_ALL) down -v --remove-orphans

# ── Infrastructure only (Postgres + Redis) ───────────────────
infra:
	$(COMPOSE_INFRA) up --build -d

infra-down:
	$(COMPOSE_INFRA) down

# ── Airflow (requires infra) ────────────────────────────────
airflow:
	$(COMPOSE_AIRFLOW) up --build -d

airflow-down:
	$(COMPOSE_AIRFLOW) down

airflow-logs:
	$(COMPOSE_AIRFLOW) logs -f airflow-apiserver airflow-scheduler airflow-worker airflow-dag-processor airflow-triggerer

# ── Backend (requires infra) ────────────────────────────────
backend:
	$(COMPOSE_BACKEND) up --build -d

backend-down:
	$(COMPOSE_BACKEND) down

backend-logs:
	$(COMPOSE_BACKEND) logs -f backend

# ── Frontend (standalone, or use: cd frontend && pnpm dev) ──
frontend:
	$(COMPOSE_FRONT) up --build -d

frontend-down:
	$(COMPOSE_FRONT) down

# ── Tests ────────────────────────────────────────────────────
test-backend:
	cd backend && python -m pytest tests/ -v

.PHONY: up down logs restart clean infra infra-down airflow airflow-down airflow-logs backend backend-down backend-logs frontend frontend-down test-backend
