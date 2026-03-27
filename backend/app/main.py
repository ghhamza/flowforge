"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.nodes import router as nodes_router
from app.api.workflows import router as workflows_router
from app.core.database import Base, engine
from app.models import workflow as _workflow_model  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup (dev-friendly)."""
    logger.info("FlowForge API starting…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FlowForge API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows_router)
app.include_router(nodes_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe for orchestration and load balancers."""
    return {"status": "ok", "service": "flowforge-api"}
