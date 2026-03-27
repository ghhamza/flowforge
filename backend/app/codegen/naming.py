"""Deterministic names for Airflow tasks and Python variables."""

import re


def slugify_label(label: str, node_id: str) -> str:
    """Human-readable Airflow task_id from label, with collision guard."""
    s = label.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_") or "task"
    if len(s) > 200:
        s = s[:200]
    short = node_id.replace("-", "")[:8]
    return f"{s}_{short}"


def py_var_for_node(node_id: str) -> str:
    """Python variable name for a node's task object."""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", node_id)
    if safe and safe[0].isdigit():
        safe = f"n_{safe}"
    return f"task_{safe}"


def task_id_for_node(node_id: str, label: str) -> str:
    """Airflow task_id (unique, deterministic)."""
    return slugify_label(label, node_id)
