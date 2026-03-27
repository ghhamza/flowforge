"""Python script node — PythonOperator."""

from dataclasses import dataclass, field
from textwrap import indent

from app.codegen.context import TaskCodegenContext
from app.codegen.xcom_snippet import xcom_pull_result_body
from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class PythonScriptNode(NodeTypeSpec):
    type: str = field(default="python_script", init=False)
    label: str = field(default="Python Script", init=False)
    category: str = field(default="Custom", init=False)
    icon: str = field(default="code", init=False)
    description: str = field(
        default="Run arbitrary Python; upstream XCom is loaded into result when connected.",
        init=False,
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="code",
                field_type="code",
                label="Python code",
                required=True,
                placeholder="out = result\nreturn out",
                description=(
                    "Python body only (no def, no imports for XCom). When an upstream task exists, "
                    "`result` is set automatically from its XCom (JSON parsed when possible), "
                    "same as Transform Data."
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

        var = py_var_for_node(ctx.node_id)
        tid = task_id_for_node(ctx.node_id, ctx.node_label)
        fn_name = f"_ff_python_{ctx.node_id.replace('-', '_')}"
        code = str(ctx.config.get("code") or "pass")
        body = indent(code.rstrip() + "\n", "    ")

        if ctx.upstream_airflow_task_ids:
            xcom = xcom_pull_result_body(ctx.upstream_airflow_task_ids[0])
            inner = (
                f"def {fn_name}(**kwargs):\n"
                "    import json\n"
                f"{xcom}"
                f"{body}"
            )
        else:
            inner = f"def {fn_name}(**kwargs):\n{body}"

        block = (
            f"{inner}\n"
            f"{var} = PythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            ")"
        )
        return block
