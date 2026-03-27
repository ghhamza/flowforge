"""Resolve upstream/downstream Airflow task_ids from canvas edges."""

from __future__ import annotations

from app.codegen.exceptions import CodegenValidationError
from app.codegen.naming import task_id_for_node


def optional_upstream_task_id_tuple(
    node_id: str,
    edges: list[tuple[str, str]],
    node_by_id: dict[str, dict],
) -> tuple[str, ...]:
    """
    First non-cron upstream task's Airflow task_id (sorted by source id).

    Empty if only cron_schedule feeds this node (no task XCom).
    """
    sources = sorted([s for s, t in edges if t == node_id])
    task_sources = [
        s for s in sources if node_by_id[s]["type"] != "cron_schedule"
    ]
    if not task_sources:
        return ()
    first = task_sources[0]
    un = node_by_id[first]
    return (task_id_for_node(first, un.get("label") or un["type"]),)


def primary_upstream_task_id_for_xcom(
    node_id: str,
    edges: list[tuple[str, str]],
    node_by_id: dict[str, dict],
) -> str:
    """Required single upstream task_id for branch / mandatory XCom pull."""
    t = optional_upstream_task_id_tuple(node_id, edges, node_by_id)
    if not t:
        raise CodegenValidationError(
            f"Node {node_id!r} must follow a task that produces XCom "
            "(connect an HTTP, Python, Manual, or Branch task upstream; "
            "cron alone is not enough)."
        )
    return t[0]


def downstream_airflow_task_ids_for_branch(
    branch_id: str,
    edges: list[tuple[str, str]],
    node_by_id: dict[str, dict],
) -> tuple[str, ...]:
    """Outgoing edges from branch node -> Airflow task_ids for BranchPythonOperator returns."""
    targets = sorted([t for s, t in edges if s == branch_id])
    if not targets:
        raise CodegenValidationError(
            "Branch node must have at least one outgoing edge to a downstream task "
            "(connect the branch to each possible next step on the canvas)."
        )
    out: list[str] = []
    for tid in targets:
        tn = node_by_id[tid]
        out.append(task_id_for_node(tid, tn.get("label") or tn["type"]))
    return tuple(out)
