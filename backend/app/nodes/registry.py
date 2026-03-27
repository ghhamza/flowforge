"""Node type registry."""

from app.nodes.base import NodeTypeSpec
from app.nodes.condition_branch import ConditionBranchNode
from app.nodes.cron_schedule import CronScheduleNode
from app.nodes.data_transform import DataTransformNode
from app.nodes.http_request import HttpRequestNode
from app.nodes.manual_trigger import ManualTriggerNode
from app.nodes.python_script import PythonScriptNode

_ALL_NODES: list[NodeTypeSpec] = [
    ManualTriggerNode(),
    CronScheduleNode(),
    HttpRequestNode(),
    DataTransformNode(),
    PythonScriptNode(),
    ConditionBranchNode(),
]

_REGISTRY: dict[str, NodeTypeSpec] = {node.type: node for node in _ALL_NODES}


def get_all_node_types() -> list[NodeTypeSpec]:
    return _ALL_NODES


def get_node_type(type_key: str) -> NodeTypeSpec | None:
    return _REGISTRY.get(type_key)
