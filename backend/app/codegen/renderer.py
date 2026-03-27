"""Assemble generated DAG Python source from parts."""

from __future__ import annotations

import textwrap

# Airflow 3: use Task SDK DAG (see upgrading_to_airflow3.rst).
DAG_IMPORT = "from airflow.sdk import DAG"
_LEGACY_DAG_IMPORTS = frozenset(
    {
        DAG_IMPORT,
        "from airflow.models.dag import DAG",
    }
)
_DAG_BODY_INDENT = "    "


def _indent_block(text: str, prefix: str = _DAG_BODY_INDENT) -> str:
    """
    Indent every logical line for placement inside `with DAG(...) as dag:`.

    Uses stdlib textwrap.indent so multi-line task blocks (HttpOperator calls,
    def/callable wrappers, BranchPythonOperator) stay consistently nested.
    """
    if not text.strip():
        return ""
    # rstrip outer newlines only; preserve inner blank lines and relative indents
    return textwrap.indent(text.rstrip("\n"), prefix)


def render_dag_file(
    *,
    docstring: str,
    imports: list[str],
    dag_id: str,
    description: str,
    schedule_repr: str,
    task_blocks: list[str],
    dependency_lines: list[str],
) -> str:
    """Build final DAG file string (deterministic formatting)."""
    other_imports = sorted(
        {i for i in imports if i.strip() and i not in _LEGACY_DAG_IMPORTS}
    )
    import_block = "\n".join([DAG_IMPORT, *other_imports]) if other_imports else DAG_IMPORT

    body_raw = "\n\n".join(task_blocks) if task_blocks else ""
    deps_raw = "\n\n".join(dependency_lines) if dependency_lines else ""

    inner_parts: list[str] = []
    if body_raw.strip():
        inner_parts.append(_indent_block(body_raw))
    if deps_raw.strip():
        inner_parts.append(_indent_block(deps_raw))

    inner_body = "\n\n".join(inner_parts) if inner_parts else ""
    inner = f"\n{inner_body}\n" if inner_body else ""

    return (
        f'"""\n{docstring}\n"""\n'
        f"from datetime import datetime\n\n"
        f"{import_block}\n\n\n"
        f"with DAG(\n"
        f'    dag_id="{dag_id}",\n'
        f"    description={repr(description)},\n"
        f"    start_date=datetime(2024, 1, 1),\n"
        f"    schedule={schedule_repr},\n"
        f"    catchup=False,\n"
        f'    tags=["flowforge"],\n'
        f") as dag:{inner}"
    )
