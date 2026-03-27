"""Pydantic schemas for workflows."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.workflow import WorkflowStatus


class NodePosition(BaseModel):
    x: float
    y: float


class NodeConfig(BaseModel):
    """Permissive dict — each node type has its own config shape."""

    model_config = {"extra": "allow"}


class CanvasNode(BaseModel):
    id: str
    type: str
    label: str
    position: NodePosition
    config: dict = Field(default_factory=dict)


class CanvasEdge(BaseModel):
    source: str
    target: str


class Canvas(BaseModel):
    nodes: list[CanvasNode] = Field(default_factory=list)
    edges: list[CanvasEdge] = Field(default_factory=list)


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    canvas: Canvas | None = None
    schedule: str | None = None
    tags: list[str] | None = None


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: WorkflowStatus
    canvas: Canvas
    schedule: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowListItem(BaseModel):
    id: uuid.UUID
    name: str
    status: WorkflowStatus
    tags: list[str]
    updated_at: datetime

    model_config = {"from_attributes": True}
