"""Pydantic schemas for node registry API."""

from pydantic import BaseModel


class ConfigFieldSchema(BaseModel):
    name: str
    field_type: str
    label: str
    required: bool
    default: object = None
    options: list[str] | None = None
    placeholder: str | None = None
    description: str | None = None


class NodeTypeSchema(BaseModel):
    type: str
    label: str
    category: str
    icon: str
    description: str
    config_fields: list[ConfigFieldSchema]
