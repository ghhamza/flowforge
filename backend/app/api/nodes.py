"""Node registry API."""

from fastapi import APIRouter

from app.nodes.base import ConfigField
from app.nodes.registry import get_all_node_types
from app.schemas.nodes import ConfigFieldSchema, NodeTypeSchema

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


def _field_to_schema(f: ConfigField) -> ConfigFieldSchema:
    return ConfigFieldSchema(
        name=f.name,
        field_type=f.field_type,
        label=f.label,
        required=f.required,
        default=f.default,
        options=f.options,
        placeholder=f.placeholder,
        description=f.description,
    )


@router.get("/registry", response_model=list[NodeTypeSchema])
async def get_registry() -> list[NodeTypeSchema]:
    out: list[NodeTypeSchema] = []
    for spec in get_all_node_types():
        out.append(
            NodeTypeSchema(
                type=spec.type,
                label=spec.label,
                category=spec.category,
                icon=spec.icon,
                description=spec.description,
                config_fields=[_field_to_schema(f) for f in spec.config_fields],
            )
        )
    return out
