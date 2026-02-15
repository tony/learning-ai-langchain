"""Tests for lesson_generator.nodes — node helpers and utilities."""

from __future__ import annotations

import typing as t

import pytest

from lesson_generator.nodes import _strip_code_fences


class StripFenceCase(t.NamedTuple):
    """Parametrized test case for _strip_code_fences."""

    test_id: str
    raw: str
    expected: str


STRIP_FENCE_CASES: list[StripFenceCase] = [
    StripFenceCase(
        test_id="no_fences_passthrough",
        raw='"""A lesson."""\n\ndef main() -> None:\n    pass\n',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="triple_fenced_no_lang",
        raw='```\n"""A lesson."""\n\ndef main() -> None:\n    pass\n```',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="triple_fenced_python_tag",
        raw='```python\n"""A lesson."""\n\ndef main() -> None:\n    pass\n```',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="quintuple_fenced",
        raw='`````python\n"""A lesson."""\n\ndef main() -> None:\n    pass\n`````',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="leading_trailing_whitespace",
        raw='  \n```python\n"""A lesson."""\n\ndef main() -> None:\n    pass\n```\n  ',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="fences_with_blank_lines",
        raw='```python\n\n"""A lesson."""\n\ndef main() -> None:\n    pass\n\n```',
        expected='"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="only_opening_fence_no_strip",
        raw='```python\n"""A lesson."""\n\ndef main() -> None:\n    pass',
        expected='```python\n"""A lesson."""\n\ndef main() -> None:\n    pass',
    ),
    StripFenceCase(
        test_id="backticks_inside_docstring_preserved",
        raw=(
            '"""A lesson with ``inline`` reST."""\n'
            "\n"
            "def example() -> str:\n"
            '    """Return ``value``."""\n'
            '    return "value"\n'
        ),
        expected=(
            '"""A lesson with ``inline`` reST."""\n'
            "\n"
            "def example() -> str:\n"
            '    """Return ``value``."""\n'
            '    return "value"'
        ),
    ),
]


@pytest.mark.parametrize(
    list(StripFenceCase._fields),
    STRIP_FENCE_CASES,
    ids=[c.test_id for c in STRIP_FENCE_CASES],
)
def test_strip_code_fences(
    test_id: str,
    raw: str,
    expected: str,
) -> None:
    """_strip_code_fences should remove outer markdown fences only."""
    assert _strip_code_fences(raw) == expected
