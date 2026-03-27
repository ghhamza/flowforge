"""Base node type specification for registry and codegen."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ConfigField:
    """Describes one field in a node's configuration panel."""

    name: str
    field_type: str  # "string", "select", "number", "code", "boolean", "key_value", "json"
    label: str
    required: bool = False
    default: object = None
    options: list[str] | None = None  # for "select" type
    placeholder: str | None = None
    description: str | None = None


@dataclass
class NodeTypeSpec(ABC):
    """Full specification of a node type — used by frontend palette and codegen."""

    type: str
    label: str
    category: str
    icon: str
    description: str
    config_fields: list[ConfigField] = field(default_factory=list)

    @abstractmethod
    def generate_imports(self) -> list[str]:
        """Return Python import lines needed for this node type."""
        ...

    @abstractmethod
    def generate_task_code(
        self, node_id: str, node_label: str, config: dict
    ) -> str:
        """Return Python code string that creates the Airflow task."""
        ...
