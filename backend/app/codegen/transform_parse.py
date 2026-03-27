"""Parse data_transform user snippet: single expression or single `return` statement."""

from __future__ import annotations

import ast

from app.codegen.exceptions import CodegenValidationError


def parse_transform_expression(code: str) -> str:
    """
    Return Python source suitable for `transformed = <expr>`.

    Accepts either one expression (e.g. list comprehension) or one `return <expr>` statement.
    """
    stripped = (code or "").strip()
    if not stripped:
        raise CodegenValidationError("data_transform requires transform_code.")
    try:
        tree = ast.parse(stripped)
    except SyntaxError as e:
        raise CodegenValidationError(f"Invalid transform expression: {e}") from e
    if len(tree.body) != 1:
        raise CodegenValidationError(
            "Transform must be a single expression or one return statement."
        )
    stmt = tree.body[0]
    if isinstance(stmt, ast.Return):
        expr = stmt.value
        if expr is None:
            raise CodegenValidationError("Transform return must include a value.")
        return ast.unparse(expr)
    if isinstance(stmt, ast.Expr):
        return ast.unparse(stmt.value)
    raise CodegenValidationError(
        "Transform must be a single expression or one return statement."
    )
