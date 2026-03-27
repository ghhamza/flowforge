# FlowForge

FlowForge is an open-source visual workflow automation platform. Draw workflows on a drag-and-drop canvas — every workflow runs as an Apache Airflow DAG under the hood.

Stack: **FastAPI** backend, **React 18** frontend (Vite, React Flow, shadcn/ui), **Apache Airflow 3** for execution, **Redis** (Celery broker), **PostgreSQL 16**, orchestrated with **Docker Compose**.

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ and [pnpm](https://pnpm.io/) (enable with `corepack enable`) for the frontend
- Python 3.11+ (for local backend development outside Docker)

## Quick Start — Full Stack

```bash
git clone <repository-url>
cd flowforge
cp .env.example .env   # optional — compose provides defaults
make up
```

Then open:

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | — |
| API health | http://localhost:8000/health | — |
| Airflow UI | http://localhost:9090 | `airflow` / `airflow` |

## Developer Workflows

The compose stack is split into isolated files so you can run only what you need:

```
docker-compose.yml            ← Infrastructure (Postgres + Redis) — always needed
docker-compose.airflow.yml    ← Airflow 3 full stack (7 services)
docker-compose.backend.yml    ← FastAPI
docker-compose.frontend.yml   ← Vite dev server
```

### Working on the frontend

```bash
make infra                 # Start Postgres + Redis
make backend               # Start FastAPI in Docker
cd frontend && pnpm dev    # Run Vite locally (fast HMR, no Docker overhead)
```

### Working on the backend / codegen

```bash
make infra                 # Start Postgres + Redis
cd backend
cp .env.example .env       # Point DATABASE_URL to localhost:5432
uvicorn app.main:app --reload
```

### Working on Airflow integration

```bash
make infra                 # Start Postgres + Redis
make airflow               # Start all Airflow services
make backend               # Start FastAPI (writes DAGs to shared volume)
```

### Full integration test

```bash
make up                    # Everything at once
```

### Makefile targets

| Target | Description |
|--------|-------------|
| `make up` | Build and start the full stack |
| `make down` | Stop all containers |
| `make logs` | Follow all service logs |
| `make restart` | Recreate all containers |
| `make clean` | Stop and remove all volumes (destructive) |
| `make infra` | Start Postgres + Redis only |
| `make airflow` | Start infra + Airflow |
| `make backend` | Start infra + FastAPI |
| `make frontend` | Start Vite dev server in Docker |
| `make test-backend` | Run backend pytest |

### Optional: Flower (Celery monitoring)

```bash
docker compose -f docker-compose.yml -f docker-compose.airflow.yml --profile flower up -d
# Then visit http://localhost:5555
```

## Architecture

- **backend/** — FastAPI service. `AIRFLOW_API_URL` points at `http://airflow-apiserver:8080/api/v2`.
- **frontend/** — Vite + React + TypeScript + Tailwind v3 + shadcn/ui. `/api` is proxied to the backend.
- **airflow/** — Image extending `apache/airflow:3.1.8`. DAGs, plugins, config, and logs are bind-mounted. Init uses the same inline bootstrap as the official compose file.
- **docker/postgres/** — Init script creates the `airflow` database and role alongside the `flowforge` app database.

The `airflow/dags/` folder is bind-mounted into both the backend and Airflow services, so the codegen engine (M2) can write DAGs where Airflow reads them.

## License

MIT — see [LICENSE](./LICENSE). Apache Airflow attribution in [NOTICE](./NOTICE).
