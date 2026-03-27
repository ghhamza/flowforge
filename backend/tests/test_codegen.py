"""Codegen unit tests — string output must stay stable for regression safety."""

import ast

import pytest

from app.codegen.engine import generate_dag
from app.codegen.exceptions import CodegenValidationError

WF_ID = "550e8400-e29b-41d4-a716-446655440000"


def test_empty_canvas_raises() -> None:
    with pytest.raises(CodegenValidationError):
        generate_dag(WF_ID, "Empty", {"nodes": [], "edges": []})


def test_single_manual_trigger() -> None:
    canvas = {
        "nodes": [
            {
                "id": "n1",
                "type": "manual_trigger",
                "label": "Start",
                "position": {"x": 0, "y": 0},
                "config": {},
            }
        ],
        "edges": [],
    }
    out = generate_dag(WF_ID, "Test", canvas)
    assert "from airflow.sdk import DAG" in out
    assert "EmptyOperator" in out
    assert "from airflow.providers.standard.operators.empty import EmptyOperator" in out
    assert 'task_id="start_n1"' in out
    assert "schedule=None" in out


def test_manual_to_http() -> None:
    canvas = {
        "nodes": [
            {
                "id": "m1",
                "type": "manual_trigger",
                "label": "Go",
                "position": {"x": 0, "y": 0},
                "config": {},
            },
            {
                "id": "h1",
                "type": "http_request",
                "label": "Fetch",
                "position": {"x": 200, "y": 0},
                "config": {
                    "url": "/api/orders",
                    "method": "GET",
                    "headers": {},
                },
            },
        ],
        "edges": [{"source": "m1", "target": "h1"}],
    }
    out = generate_dag(WF_ID, "Orders", canvas)
    assert (
        "from airflow.providers.standard.operators.python import PythonOperator" in out
    )
    assert "urllib.request" in out
    assert "task_m1 >> task_h1" in out
    assert "/api/orders" in out


def test_cron_and_http_no_empty_for_cron() -> None:
    canvas = {
        "nodes": [
            {
                "id": "c1",
                "type": "cron_schedule",
                "label": "Daily",
                "position": {"x": 0, "y": 0},
                "config": {"cron_expression": "0 9 * * *"},
            },
            {
                "id": "h1",
                "type": "http_request",
                "label": "Ping",
                "position": {"x": 200, "y": 0},
                "config": {
                    "url": "/health",
                    "method": "GET",
                    "headers": {},
                },
            },
        ],
        "edges": [{"source": "c1", "target": "h1"}],
    }
    out = generate_dag(WF_ID, "Cron job", canvas, schedule=None)
    assert "schedule=" in out and "0 9 * * *" in out
    assert "EmptyOperator" not in out
    assert "PythonOperator" in out
    assert "urllib.request" in out


def test_branch_two_downstream() -> None:
    canvas = {
        "nodes": [
            {
                "id": "m1",
                "type": "manual_trigger",
                "label": "Manual",
                "position": {"x": 0, "y": 0},
                "config": {},
            },
            {
                "id": "b1",
                "type": "condition_branch",
                "label": "Pick",
                "position": {"x": 100, "y": 0},
                "config": {"condition_code": "return 'task_h1'"},
            },
            {
                "id": "h1",
                "type": "http_request",
                "label": "A",
                "position": {"x": 200, "y": -50},
                "config": {
                    "url": "/a",
                    "method": "GET",
                    "headers": {},
                },
            },
            {
                "id": "h2",
                "type": "http_request",
                "label": "B",
                "position": {"x": 200, "y": 50},
                "config": {
                    "url": "/b",
                    "method": "GET",
                    "headers": {},
                },
            },
        ],
        "edges": [
            {"source": "m1", "target": "b1"},
            {"source": "b1", "target": "h1"},
            {"source": "b1", "target": "h2"},
        ],
    }
    out = generate_dag(WF_ID, "Branch", canvas)
    assert (
        "from airflow.providers.standard.operators.python import BranchPythonOperator"
        in out
    )
    assert "BranchPythonOperator" in out
    assert "task_b1 >> [task_h1, task_h2]" in out


def test_python_script_wraps_code() -> None:
    canvas = {
        "nodes": [
            {
                "id": "m1",
                "type": "manual_trigger",
                "label": "M",
                "position": {"x": 0, "y": 0},
                "config": {},
            },
            {
                "id": "p1",
                "type": "python_script",
                "label": "Run",
                "position": {"x": 100, "y": 0},
                "config": {"code": "x = 1\nreturn x"},
            },
        ],
        "edges": [{"source": "m1", "target": "p1"}],
    }
    out = generate_dag(WF_ID, "Py", canvas)
    assert (
        "from airflow.providers.standard.operators.python import PythonOperator" in out
    )
    assert "PythonOperator" in out
    assert "def _ff_python_p1" in out
    assert "return x" in out


def test_determinism() -> None:
    canvas_ok = {
        "nodes": [
            {
                "id": "m1",
                "type": "manual_trigger",
                "label": "Only",
                "position": {"x": 0, "y": 0},
                "config": {},
            }
        ],
        "edges": [],
    }
    a = generate_dag(WF_ID, "Same", canvas_ok)
    b = generate_dag(WF_ID, "Same", canvas_ok)
    assert a == b


def test_generated_dag_is_valid_python_http_plus_branch() -> None:
    """Regression: multi-line tasks + deps must parse (no stray dedent / unexpected indent)."""
    canvas = {
        "nodes": [
            {
                "id": "c1",
                "type": "cron_schedule",
                "label": "C",
                "position": {"x": 0, "y": 0},
                "config": {"cron_expression": "* * * * *"},
            },
            {
                "id": "h1",
                "type": "http_request",
                "label": "HTTP Request",
                "position": {"x": 0, "y": 0},
                "config": {
                    "url": "/todos",
                    "method": "GET",
                    "headers": {},
                },
            },
            {
                "id": "b1",
                "type": "condition_branch",
                "label": "Condition Branch",
                "position": {"x": 0, "y": 0},
                "config": {"condition_code": "return task_id"},
            },
        ],
        "edges": [
            {"source": "c1", "target": "h1"},
            {"source": "h1", "target": "b1"},
        ],
    }
    out = generate_dag(WF_ID, "test", canvas)
    ast.parse(out)


def test_cycle_raises() -> None:
    canvas = {
        "nodes": [
            {
                "id": "m1",
                "type": "manual_trigger",
                "label": "M",
                "position": {"x": 0, "y": 0},
                "config": {},
            },
            {
                "id": "a",
                "type": "http_request",
                "label": "A",
                "position": {"x": 0, "y": 0},
                "config": {
                    "url": "/a",
                    "method": "GET",
                    "headers": {},
                },
            },
            {
                "id": "b",
                "type": "http_request",
                "label": "B",
                "position": {"x": 0, "y": 0},
                "config": {
                    "url": "/b",
                    "method": "GET",
                    "headers": {},
                },
            },
        ],
        "edges": [
            {"source": "m1", "target": "a"},
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ],
    }
    with pytest.raises(CodegenValidationError):
        generate_dag(WF_ID, "Cycle", canvas)
