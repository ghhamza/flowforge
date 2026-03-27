"""Lightweight API tests without DB lifespan (router-only app)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.nodes import router as nodes_router


def _minimal_app() -> FastAPI:
    app = FastAPI()
    app.include_router(nodes_router)
    return app


def test_nodes_registry_shape() -> None:
    client = TestClient(_minimal_app())
    r = client.get("/api/nodes/registry")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 5
    types = {item["type"] for item in data}
    assert "http_request" in types
    assert "manual_trigger" in types
