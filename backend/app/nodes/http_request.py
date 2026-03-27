"""HTTP request node — PythonOperator + stdlib urllib (no Airflow Connection required)."""

import json
from dataclasses import dataclass, field

from app.nodes.base import ConfigField, NodeTypeSpec


@dataclass
class HttpRequestNode(NodeTypeSpec):
    type: str = field(default="http_request", init=False)
    label: str = field(default="HTTP Request", init=False)
    category: str = field(default="HTTP", init=False)
    icon: str = field(default="globe", init=False)
    description: str = field(
        default="HTTP call via urllib (no http_conn_id; works on any Airflow worker).",
        init=False,
    )
    config_fields: list[ConfigField] = field(
        default_factory=lambda: [
            ConfigField(
                name="url",
                field_type="string",
                label="URL or path",
                required=True,
                placeholder="https://api.example.com/data",
            ),
            ConfigField(
                name="base_url",
                field_type="string",
                label="Base URL (for relative paths)",
                required=False,
                default="https://jsonplaceholder.typicode.com",
                description=(
                    "If URL does not start with http:// or https://, it is appended to this base."
                ),
            ),
            ConfigField(
                name="method",
                field_type="select",
                label="Method",
                required=False,
                default="GET",
                options=["GET", "POST", "PUT", "DELETE", "PATCH"],
            ),
            ConfigField(
                name="headers",
                field_type="key_value",
                label="Headers",
                required=False,
                default={},
            ),
            ConfigField(
                name="body",
                field_type="json",
                label="JSON body",
                required=False,
                default=None,
            ),
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
        fn_name = f"_ff_http_{node_id.replace('-', '_')}"

        url_raw = str(config.get("url") or "/")
        method = str(config.get("method") or "GET").upper()
        base = str(config.get("base_url") or "https://jsonplaceholder.typicode.com").rstrip(
            "/"
        )
        headers = config.get("headers") or {}
        if not isinstance(headers, dict):
            headers = {}
        body = config.get("body")

        if url_raw.startswith("http://") or url_raw.startswith("https://"):
            full_url = url_raw
        else:
            path = url_raw if url_raw.startswith("/") else f"/{url_raw}"
            full_url = base + path

        headers_json = json.dumps(headers, sort_keys=True)
        if body is not None:
            body_json = json.dumps(body)
            body_setup = f"    body_obj = json.loads({repr(body_json)})"
        else:
            body_setup = "    body_obj = None"

        return (
            f"def {fn_name}(**kwargs):\n"
            "    import json\n"
            "    import urllib.request\n"
            f"    url = {repr(full_url)}\n"
            f"    method = {repr(method)}\n"
            f"    headers = json.loads({repr(headers_json)})\n"
            f"{body_setup}\n"
            "    body_data = None\n"
            "    extra = {}\n"
            "    if body_obj is not None and method in ("
            '"POST", "PUT", "PATCH", "DELETE"):\n'
            "        if isinstance(body_obj, (dict, list)):\n"
            "            body_data = json.dumps(body_obj).encode('utf-8')\n"
            '            extra["Content-Type"] = "application/json"\n'
            "        else:\n"
            "            body_data = str(body_obj).encode('utf-8')\n"
            "    merged = {**headers, **extra}\n"
            "    req = urllib.request.Request("
            "url, data=body_data, headers=merged, method=method)\n"
            "    with urllib.request.urlopen(req, timeout=120) as resp:\n"
            "        return resp.read().decode()\n"
            "\n"
            f"{var} = PythonOperator(\n"
            f'    task_id="{tid}",\n'
            f"    python_callable={fn_name},\n"
            ")"
        )
