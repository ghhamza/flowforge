"""Condition / branch node — BranchPythonOperator with upstream XCom in `result`."""

from dataclasses import dataclass, field
from textwrap import indent

from app.codegen.branch_validation import validate_branch_condition_returns
from app.codegen.context import TaskCodegenContext
from app.codegen.xcom_snippet import xcom_pull_result_body
from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class ConditionBranchNode(NodeTypeSpec):
    type: str = field(default="condition_branch", init=False)
    label: str = field(default="Condition Branch", init=False)
    category: str = field(default="Logic", init=False)
    icon: str = field(default="git-branch", init=False)
    description: str = field(
        default="Branch using upstream XCom as `result`; return downstream task_ids.",
        init=False,
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="condition_code",
                field_type="code",
                label="Branch logic",
                required=True,
                placeholder=(
                    "if result and result[0].get('completed'):\n"
                    "    return 'downstream_task_id_a'\n"
                    "return 'downstream_task_id_b'"
                ),
                description=(
                    "Only branching logic: use `result` (parsed upstream XCom). "
                    "Each return must be a string literal matching a downstream task's id."
                ),
            )
        ],
        init=False,
    )

    def generate_imports(self) -> list[str]:
        return [
            "from airflow.providers.standard.operators.python import BranchPythonOperator",
        ]

    def generate_task_code(self, ctx: TaskCodegenContext) -> str:
        from app.codegen.naming import py_var_for_node, task_id_for_node

        upstream_tid = ctx.upstream_airflow_task_ids[0]

        validate_branch_condition_returns(
            str(ctx.config.get("condition_code") or ""),
            frozenset(ctx.downstream_airflow_task_ids),
        )

        var = py_var_for_node(ctx.node_id)
        tid = task_id_for_node(ctx.node_id, ctx.node_label)
        fn_name = f"_ff_branch_{ctx.node_id.replace('-', '_')}"
        user = indent(str(ctx.config.get("condition_code") or "").strip() + "\n", "    ")
        xcom = xcom_pull_result_body(upstream_tid)
        block = (
            f"def {fn_name}(**kwargs):\n"
            "    import json\n"
            f"{xcom}"
            f"{user}\n"
            f"{var} = BranchPythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            ")"
        )
        return block
