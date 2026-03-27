"""Python script node — PythonOperator."""

from dataclasses import dataclass, field
from textwrap import indent

from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class PythonScriptNode(NodeTypeSpec):
    type: str = field(default="python_script", init=False)
    label: str = field(default="Python Script", init=False)
    category: str = field(default="Custom", init=False)
    icon: str = field(default="code", init=False)
    description: str = field(
        default="Run Python code in the worker (use kwargs['ti'] for XCom).", init=False
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="code",
                field_type="code",
                label="Python code",
                required=True,
                placeholder="# Your Python code here\nresult = 'hello'",
                description="Python code to execute. Use kwargs['ti'] for XCom.",
            )
        ],
        init=False,
    )

    def generate_imports(self) -> list[str]:
        return [
            "from airflow.providers.standard.operators.python import PythonOperator",
        ]

    def generate_task_code(
        self, node_id: str, node_label: str, config: dict
    ) -> str:
        from app.codegen.naming import py_var_for_node, task_id_for_node

        var = py_var_for_node(node_id)
        tid = task_id_for_node(node_id, node_label)
        fn_name = f"_ff_python_{node_id.replace('-', '_')}"
        code = str(config.get("code") or "pass")
        body = indent(code.rstrip() + "\n", "    ")
        block = (
            f"def {fn_name}(**kwargs):\n"
            f"{body}\n\n"
            f"{var} = PythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            f")"
        )
        return block
