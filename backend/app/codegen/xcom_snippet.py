"""Reusable XCom pull + JSON parse into `result` for generated callables."""

from __future__ import annotations


def xcom_pull_result_body(upstream_airflow_task_id: str) -> str:
    """
    Indented lines (inside def) after `import json`.

    Sets `ti`, `raw`, and `result`.
    """
    return (
        "    ti = kwargs['ti']\n"
        f"    raw = ti.xcom_pull(task_ids={upstream_airflow_task_id!r})\n"
        "    try:\n"
        "        result = json.loads(raw) if isinstance(raw, str) else raw\n"
        "    except (json.JSONDecodeError, TypeError):\n"
        "        result = raw\n"
    )
