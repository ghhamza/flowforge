"""Cron schedule trigger — sets DAG schedule, no task object."""

from dataclasses import dataclass, field

from app.codegen.context import TaskCodegenContext
from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class CronScheduleNode(NodeTypeSpec):
    type: str = field(default="cron_schedule", init=False)
    label: str = field(default="Cron Schedule", init=False)
    category: str = field(default="Triggers", init=False)
    icon: str = field(default="clock", init=False)
    description: str = field(
        default="Run the DAG on a cron expression (no extra task).", init=False
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="cron_expression",
                field_type="string",
                label="Cron expression",
                required=True,
                placeholder="0 9 * * *",
                description="Standard five-field cron string passed to the DAG schedule.",
            )
        ],
        init=False,
    )

    def generate_imports(self) -> list[str]:
        return []

    def generate_task_code(self, ctx: TaskCodegenContext) -> str:
        return ""
