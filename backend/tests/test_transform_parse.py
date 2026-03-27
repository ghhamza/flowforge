"""data_transform expression parsing."""

import pytest

from app.codegen.exceptions import CodegenValidationError
from app.codegen.transform_parse import parse_transform_expression


def test_expression_list_comp() -> None:
    out = parse_transform_expression("[x for x in result]")
    assert out == "[x for x in result]"


def test_return_stripped() -> None:
    out = parse_transform_expression("return {'a': 1}")
    assert out == "{'a': 1}"


def test_empty_raises() -> None:
    with pytest.raises(CodegenValidationError):
        parse_transform_expression("")


def test_multiple_statements_raises() -> None:
    with pytest.raises(CodegenValidationError):
        parse_transform_expression("x = 1\nreturn x")
