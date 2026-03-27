"""Branch condition return validation."""

import pytest

from app.codegen.branch_validation import validate_branch_condition_returns
from app.codegen.exceptions import CodegenValidationError


def test_branch_return_must_match_allowed() -> None:
    with pytest.raises(CodegenValidationError):
        validate_branch_condition_returns(
            "return 'wrong_id'\n",
            frozenset({"a_h1", "b_h2"}),
        )


def test_branch_return_ok() -> None:
    validate_branch_condition_returns(
        "return 'a_h1'\n",
        frozenset({"a_h1", "b_h2"}),
    )
