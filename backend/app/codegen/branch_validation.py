"""Validate branch condition snippets: return literals must match downstream task_ids."""

from __future__ import annotations

import ast

from app.codegen.exceptions import CodegenValidationError


def validate_branch_condition_returns(code: str, allowed: frozenset[str]) -> None:
    """
    Ensure every `return` of a string constant references an allowed task_id.

    Dynamic returns (variables, f-strings) are rejected so codegen stays safe.
    """
    if not allowed:
        raise CodegenValidationError(
            "Branch node must have at least one outgoing edge to a downstream task "
            "(connect the branch to each possible next step on the canvas)."
        )
    stripped = code.strip()
    if not stripped:
        raise CodegenValidationError("condition_branch requires condition logic.")

    try:
        tree = ast.parse(stripped)
    except SyntaxError as e:
        raise CodegenValidationError(f"Invalid branch condition Python: {e}") from e

    found_return = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            found_return = True
            if node.value is None:
                raise CodegenValidationError(
                    "Branch condition cannot use bare `return`; return a downstream "
                    f"task_id string, one of: {sorted(allowed)}"
                )
            tid = _string_constant(node.value)
            if tid is None:
                raise CodegenValidationError(
                    "Branch condition must use string literal returns with downstream "
                    f"task_ids only (no variables or f-strings). Allowed: {sorted(allowed)}"
                )
            if tid not in allowed:
                raise CodegenValidationError(
                    f"Return {tid!r} is not a downstream task_id. Allowed: {sorted(allowed)}"
                )

    if not found_return:
        raise CodegenValidationError(
            "Branch condition must contain at least one return with a task_id string."
        )


def _string_constant(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None
