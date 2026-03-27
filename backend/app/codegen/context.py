"""Per-task context passed from the codegen engine into node generators."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskCodegenContext:
    """Upstream/downstream Airflow task_ids resolved from the canvas graph."""

    node_id: str
    node_label: str
    config: dict
    # Airflow task_id strings (slugify_label), sorted by upstream node id
    upstream_airflow_task_ids: tuple[str, ...]
    # For condition_branch: valid return targets; sorted by target node id
    downstream_airflow_task_ids: tuple[str, ...]
