"""Workflow CRUD, publish, and unpublish."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.codegen.engine import generate_dag
from app.codegen.exceptions import CodegenValidationError
from app.core.airflow_client import AirflowClient
from app.core.config import settings
from app.core.database import get_db
from app.models.workflow import Workflow, WorkflowStatus
from app.schemas.workflow import (
    Canvas,
    WorkflowCreate,
    WorkflowListItem,
    WorkflowResponse,
    WorkflowUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


def _dag_filename(wid: uuid.UUID) -> str:
    return f"flowforge_{wid}.py"


def _workflow_to_response(w: Workflow) -> WorkflowResponse:
    tags = w.tags if isinstance(w.tags, list) else []
    return WorkflowResponse(
        id=w.id,
        name=w.name,
        description=w.description,
        status=w.status,
        canvas=Canvas.model_validate(w.canvas),
        schedule=w.schedule,
        tags=list(tags),
        created_at=w.created_at,
        updated_at=w.updated_at,
    )


@router.get("", response_model=list[WorkflowListItem])
async def list_workflows(db: AsyncSession = Depends(get_db)) -> list[WorkflowListItem]:
    result = await db.execute(select(Workflow).order_by(Workflow.updated_at.desc()))
    rows = result.scalars().all()
    return [WorkflowListItem.model_validate(r) for r in rows]


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: WorkflowCreate, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    w = Workflow(
        name=body.name,
        description=body.description,
        status=WorkflowStatus.DRAFT,
        canvas={"nodes": [], "edges": []},
        schedule=None,
        tags=[],
    )
    db.add(w)
    await db.commit()
    await db.refresh(w)
    return _workflow_to_response(w)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    w = await db.get(Workflow, workflow_id)
    if not w:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflow_to_response(w)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    w = await db.get(Workflow, workflow_id)
    if not w:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if body.canvas is not None and w.status == WorkflowStatus.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail="Cannot change canvas while published; unpublish first.",
        )

    if body.name is not None:
        w.name = body.name
    if body.description is not None:
        w.description = body.description
    if body.canvas is not None:
        w.canvas = body.canvas.model_dump(mode="json")
    if body.schedule is not None:
        w.schedule = body.schedule
    if body.tags is not None:
        w.tags = body.tags

    await db.commit()
    await db.refresh(w)
    return _workflow_to_response(w)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    w = await db.get(Workflow, workflow_id)
    if not w:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if w.status == WorkflowStatus.PUBLISHED:
        path = Path(settings.DAGS_DIR) / _dag_filename(w.id)
        if path.is_file():
            path.unlink()

    db.delete(w)
    await db.commit()

    client = AirflowClient()
    await client.trigger_dag_parse(_dag_filename(workflow_id).replace(".py", ""))


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
async def publish_workflow(
    workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    w = await db.get(Workflow, workflow_id)
    if not w:
        raise HTTPException(status_code=404, detail="Workflow not found")

    canvas = w.canvas if isinstance(w.canvas, dict) else {}
    nodes = canvas.get("nodes") or []
    if not nodes:
        raise HTTPException(status_code=400, detail="Canvas must have at least one node.")

    try:
        src = generate_dag(
            str(w.id),
            w.name,
            canvas,
            schedule=w.schedule,
        )
    except CodegenValidationError as e:
        logger.warning("Publish blocked: codegen validation failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e

    Path(settings.DAGS_DIR).mkdir(parents=True, exist_ok=True)
    path = Path(settings.DAGS_DIR) / _dag_filename(w.id)
    path.write_text(src, encoding="utf-8")

    client = AirflowClient()
    await client.trigger_dag_parse(_dag_filename(w.id))

    w.status = WorkflowStatus.PUBLISHED
    await db.commit()
    await db.refresh(w)
    return _workflow_to_response(w)


@router.post("/{workflow_id}/unpublish", response_model=WorkflowResponse)
async def unpublish_workflow(
    workflow_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    w = await db.get(Workflow, workflow_id)
    if not w:
        raise HTTPException(status_code=404, detail="Workflow not found")

    path = Path(settings.DAGS_DIR) / _dag_filename(w.id)
    if path.is_file():
        path.unlink()

    client = AirflowClient()
    await client.trigger_dag_parse(_dag_filename(w.id))

    w.status = WorkflowStatus.DRAFT
    await db.commit()
    await db.refresh(w)
    return _workflow_to_response(w)
