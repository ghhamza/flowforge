"""Pure DAG codegen: canvas JSON -> Airflow DAG Python source."""

from __future__ import annotations

from collections import defaultdict, deque

from app.codegen.context import TaskCodegenContext
from app.codegen.exceptions import CodegenValidationError
from app.codegen.graph_resolution import (
    downstream_airflow_task_ids_for_branch,
    optional_upstream_task_id_tuple,
    primary_upstream_task_id_for_xcom,
)
from app.codegen.naming import py_var_for_node
from app.codegen.renderer import render_dag_file
from app.nodes.registry import get_node_type

TRIGGER_TYPES = frozenset({"manual_trigger", "cron_schedule"})
TASK_TYPES = frozenset(
    {
        "manual_trigger",
        "http_request",
        "data_transform",
        "python_script",
        "condition_branch",
    }
)
NON_TASK_TYPES = frozenset({"cron_schedule"})


def _build_task_context(
    n: dict,
    edges: list[tuple[str, str]],
    node_by_id: dict[str, dict],
) -> TaskCodegenContext:
    nid = n["id"]
    label = n.get("label") or n["type"]
    cfg = n.get("config") or {}
    if not isinstance(cfg, dict):
        cfg = {}

    ntype = n["type"]
    if ntype == "condition_branch":
        up = (primary_upstream_task_id_for_xcom(nid, edges, node_by_id),)
        down = downstream_airflow_task_ids_for_branch(nid, edges, node_by_id)
        return TaskCodegenContext(
            node_id=nid,
            node_label=label,
            config=cfg,
            upstream_airflow_task_ids=up,
            downstream_airflow_task_ids=down,
        )

    if ntype == "data_transform":
        up = (primary_upstream_task_id_for_xcom(nid, edges, node_by_id),)
        return TaskCodegenContext(
            node_id=nid,
            node_label=label,
            config=cfg,
            upstream_airflow_task_ids=up,
            downstream_airflow_task_ids=(),
        )

    if ntype in ("python_script", "http_request"):
        up = optional_upstream_task_id_tuple(nid, edges, node_by_id)
        return TaskCodegenContext(
            node_id=nid,
            node_label=label,
            config=cfg,
            upstream_airflow_task_ids=up,
            downstream_airflow_task_ids=(),
        )

    return TaskCodegenContext(
        node_id=nid,
        node_label=label,
        config=cfg,
        upstream_airflow_task_ids=(),
        downstream_airflow_task_ids=(),
    )


def _has_cycle(node_ids: set[str], edges: list[tuple[str, str]]) -> bool:
    adj: dict[str, list[str]] = defaultdict(list)
    for s, t in edges:
        adj[s].append(t)
    visited: set[str] = set()
    stack: set[str] = set()

    def visit(u: str) -> bool:
        if u in stack:
            return True
        if u in visited:
            return False
        visited.add(u)
        stack.add(u)
        for v in sorted(adj[u]):
            if visit(v):
                return True
        stack.remove(u)
        return False

    for nid in sorted(node_ids):
        if nid not in visited:
            if visit(nid):
                return True
    return False


def _validate_and_prepare(
    canvas: dict,
) -> tuple[list[dict], list[tuple[str, str]], str | None]:
    nodes = canvas.get("nodes") or []
    edges_raw = canvas.get("edges") or []
    if not nodes:
        raise CodegenValidationError("Canvas has no nodes.")

    node_by_id = {n["id"]: n for n in nodes}
    if len(node_by_id) != len(nodes):
        raise CodegenValidationError("Duplicate node ids in canvas.")

    for e in edges_raw:
        s, t = e.get("source"), e.get("target")
        if s not in node_by_id or t not in node_by_id:
            raise CodegenValidationError("Edge references unknown node.")
        if node_by_id[t]["type"] == "cron_schedule":
            raise CodegenValidationError("Invalid edge targeting cron_schedule.")

    edges = [(e["source"], e["target"]) for e in edges_raw]

    task_nodes = [n for n in nodes if n["type"] in TASK_TYPES]
    if not task_nodes:
        raise CodegenValidationError("Canvas must contain at least one task node.")

    triggers = {n["id"] for n in nodes if n["type"] in TRIGGER_TYPES}
    if not triggers:
        raise CodegenValidationError("Canvas must include a trigger node.")

    # Reachability from triggers
    adj_f = defaultdict(list)
    for s, t in edges:
        adj_f[s].append(t)
    seen: set[str] = set()
    dq: deque[str] = deque(sorted(triggers))
    while dq:
        u = dq.popleft()
        if u in seen:
            continue
        seen.add(u)
        for v in sorted(adj_f[u]):
            dq.append(v)
    for nid in sorted(node_by_id.keys()):
        if nid not in seen:
            raise CodegenValidationError(f"Orphan node not reachable from triggers: {nid}")

    node_ids = set(node_by_id.keys())
    if _has_cycle(node_ids, edges):
        raise CodegenValidationError("Canvas graph contains a cycle.")

    # Cron schedule for DAG (first cron node by id)
    cron_nodes = sorted(
        [n for n in nodes if n["type"] == "cron_schedule"], key=lambda x: x["id"]
    )
    cron_schedule: str | None = None
    if cron_nodes:
        expr = (cron_nodes[0].get("config") or {}).get("cron_expression")
        if not expr or not str(expr).strip():
            raise CodegenValidationError("cron_schedule node requires cron_expression.")
        cron_schedule = str(expr).strip()

    return nodes, edges, cron_schedule


def generate_dag(
    workflow_id: str,
    workflow_name: str,
    canvas: dict,
    schedule: str | None = None,
) -> str:
    """
    Pure function: canvas JSON -> Python DAG source code string.

    Deterministic: same input always produces same output.
    Raises CodegenValidationError if the graph is invalid.
    """
    nodes, edges, cron_from_canvas = _validate_and_prepare(canvas)

    effective_schedule = schedule if schedule else cron_from_canvas
    schedule_repr = "None" if effective_schedule is None else repr(effective_schedule)

    node_by_id = {n["id"]: n for n in nodes}
    imports: list[str] = []
    task_blocks: list[str] = []

    # Task nodes only (exclude cron_schedule); sorted by id
    task_node_list = sorted(
        [n for n in nodes if n["type"] in TASK_TYPES],
        key=lambda x: x["id"],
    )
    for n in task_node_list:
        spec = get_node_type(n["type"])
        if spec is None:
            raise CodegenValidationError(f"Unknown node type: {n['type']}")
        imports.extend(spec.generate_imports())
        ctx = _build_task_context(n, edges, node_by_id)
        code = spec.generate_task_code(ctx)
        task_blocks.append(code)

    # Dependencies (skip edges whose source is cron_schedule — targets are DAG roots)
    out_by_src: dict[str, list[str]] = defaultdict(list)
    for s, t in sorted(edges, key=lambda p: (p[0], p[1])):
        if node_by_id[s]["type"] == "cron_schedule":
            continue
        out_by_src[s].append(t)
    for k in out_by_src:
        out_by_src[k] = sorted(set(out_by_src[k]))

    dep_lines: list[str] = []
    for src in sorted(out_by_src.keys()):
        tgts = out_by_src[src]
        stype = node_by_id[src]["type"]
        if stype == "condition_branch" and len(tgts) > 1:
            lhs = py_var_for_node(src)
            rhs_list = [py_var_for_node(t) for t in tgts]
            dep_lines.append(f"{lhs} >> [{', '.join(rhs_list)}]")
        else:
            for tgt in tgts:
                dep_lines.append(f"{py_var_for_node(src)} >> {py_var_for_node(tgt)}")

    doc = (
        f"Auto-generated by FlowForge. Do not edit manually.\n"
        f"Workflow: {workflow_name}\n"
        f"ID: {workflow_id}"
    )
    dag_id = f"flowforge_{workflow_id.replace('-', '')}"

    return render_dag_file(
        docstring=doc,
        imports=imports,
        dag_id=dag_id,
        description=workflow_name,
        schedule_repr=schedule_repr,
        task_blocks=task_blocks,
        dependency_lines=dep_lines,
    )
