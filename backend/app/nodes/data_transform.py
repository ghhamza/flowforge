"""Data transform node — reshape upstream XCom via a Python expression."""

from dataclasses import dataclass, field
from textwrap import indent

from app.codegen.context import TaskCodegenContext
from app.codegen.transform_parse import parse_transform_expression
from app.codegen.xcom_snippet import xcom_pull_result_body
from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class DataTransformNode(NodeTypeSpec):
    type: str = field(default="data_transform", init=False)
    label: str = field(default="Transform Data", init=False)
    category: str = field(default="Data", init=False)
    icon: str = field(default="arrow-left-right", init=False)
    description: str = field(
        default="Transform upstream data. The variable result contains the previous node's output.",
        init=False,
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="transform_code",
                field_type="code",
                label="Transform expression",
                required=True,
                placeholder="[{'title': item['title']} for item in result]",
                description=(
                    "Available variables: result (upstream data). Return the transformed data."
                ),
            )
        ],
        init=False,
    )

    def generate_imports(self) -> list[str]:
        return [
            "from airflow.providers.standard.operators.python import PythonOperator",
        ]

    def generate_task_code(self, ctx: TaskCodegenContext) -> str:
        from app.codegen.naming import py_var_for_node, task_id_for_node

        upstream_tid = ctx.upstream_airflow_task_ids[0]
        expr_src = parse_transform_expression(str(ctx.config.get("transform_code") or ""))
        expr_block = indent(f"transformed = {expr_src}\n", "    ")

        var = py_var_for_node(ctx.node_id)
        tid = task_id_for_node(ctx.node_id, ctx.node_label)
        fn_name = f"_ff_transform_{ctx.node_id.replace('-', '_')}"
        xcom = xcom_pull_result_body(upstream_tid)

        tail = (
            "    print(json.dumps(transformed, indent=2) if isinstance(transformed, (dict, list)) "
            "else str(transformed))\n"
            "    return json.dumps(transformed) if isinstance(transformed, (dict, list)) "
            "else transformed\n"
        )

        block = (
            f"def {fn_name}(**kwargs):\n"
            "    import json\n"
            f"{xcom}"
            f"{expr_block}"
            f"{tail}"
            f"{var} = PythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            ")"
        )
        return block
