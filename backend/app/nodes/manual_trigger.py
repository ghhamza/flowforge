"""Manual trigger node — EmptyOperator."""

from dataclasses import dataclass, field

from app.codegen.context import TaskCodegenContext
from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class ManualTriggerNode(NodeTypeSpec):
    type: str = field(default="manual_trigger", init=False)
    label: str = field(default="Manual Trigger", init=False)
    category: str = field(default="Triggers", init=False)
    icon: str = field(default="play", init=False)
    description: str = field(default="Start the workflow manually in Airflow.", init=False)
    config_fields: list[ConfigField] = field(default_factory=list, init=False)

    def generate_imports(self) -> list[str]:
        return [
            "from airflow.providers.standard.operators.empty import EmptyOperator",
        ]

    def generate_task_code(self, ctx: TaskCodegenContext) -> str:
        from app.codegen.naming import py_var_for_node, task_id_for_node

        var = py_var_for_node(ctx.node_id)
        tid = task_id_for_node(ctx.node_id, ctx.node_label)
        return (
            f"{var} = EmptyOperator(\n"
            f'    task_id="{tid}",\n'
            f")"
        )
