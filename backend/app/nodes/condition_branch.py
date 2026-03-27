"""Condition / branch node — BranchPythonOperator."""

from dataclasses import dataclass, field
from textwrap import indent

from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class ConditionBranchNode(NodeTypeSpec):
    type: str = field(default="condition_branch", init=False)
    label: str = field(default="Condition Branch", init=False)
    category: str = field(default="Logic", init=False)
    icon: str = field(default="git-branch", init=False)
    description: str = field(
        default="Branch to a downstream task based on Python logic.", init=False
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="condition_code",
                field_type="code",
                label="Branch condition",
                required=True,
                placeholder=(
                    "# Return the task_id of the branch to follow\nreturn 'task_a'"
                ),
                description="Must return the task_id string of the next task to run.",
            )
        ],
        init=False,
    )

    def generate_imports(self) -> list[str]:
        return [
            "from airflow.providers.standard.operators.python import BranchPythonOperator",
        ]

    def generate_task_code(
        self, node_id: str, node_label: str, config: dict
    ) -> str:
        from app.codegen.naming import py_var_for_node, task_id_for_node

        var = py_var_for_node(node_id)
        tid = task_id_for_node(node_id, node_label)
        fn_name = f"_ff_branch_{node_id.replace('-', '_')}"
        code = str(config.get("condition_code") or "return None")
        body = indent(code.rstrip() + "\n", "    ")
        block = (
            f"def {fn_name}(**kwargs):\n"
            f"{body}\n\n"
            f"{var} = BranchPythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            f")"
        )
        return block
