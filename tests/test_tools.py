"""Tests for lesson_generator.tools — filesystem and validation, no LLM."""

from __future__ import annotations

import pathlib

import pytest

from lesson_generator.models import DomainConfig, PedagogyStyle, ProjectType
from lesson_generator.tools import (
    list_existing_lessons,
    next_lesson_number,
    read_template,
    validate_in_temp,
    write_lesson,
)


def test_read_template_reads_project_template(
    test_domain_config: DomainConfig,
) -> None:
    """read_template should return content from the project template file."""
    result = read_template(test_domain_config)
    assert "Template" in result


def test_read_template_fallback_when_no_project() -> None:
    """read_template should fall back to built-in when no project_path set."""
    config = DomainConfig(
        name="noproject",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    result = read_template(config)
    assert "demonstrate_concept" in result


def test_read_template_fallback_when_template_missing(
    tmp_path: pathlib.Path,
) -> None:
    """read_template should fall back to built-in when template file is absent."""
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=tmp_path,
        template_path="nonexistent.py",
    )
    result = read_template(config)
    # Should fall back to built-in
    assert "demonstrate_concept" in result


def test_list_existing_lessons_lists_py_files(
    test_domain_config: DomainConfig,
) -> None:
    """list_existing_lessons should find .py lesson files."""
    lessons = list_existing_lessons(test_domain_config)
    assert "001_intro.py" in lessons
    assert "002_basics.py" in lessons


def test_list_existing_lessons_excludes_init(
    test_domain_config: DomainConfig,
) -> None:
    """list_existing_lessons should exclude __init__.py."""
    lessons = list_existing_lessons(test_domain_config)
    assert "__init__.py" not in lessons


def test_list_existing_lessons_empty_when_no_project() -> None:
    """list_existing_lessons should return [] when no project_path set."""
    config = DomainConfig(
        name="none",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    assert list_existing_lessons(config) == []


def test_list_existing_lessons_handles_nested_dirs(
    tmp_path: pathlib.Path,
) -> None:
    """list_existing_lessons should find lessons in nested directories."""
    src = tmp_path / "src" / "subdir"
    src.mkdir(parents=True)
    (src / "001_nested.py").write_text("# nested", encoding="utf-8")
    config = DomainConfig(
        name="nested",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=tmp_path,
        lesson_dir="src",
    )
    lessons = list_existing_lessons(config)
    assert any("001_nested.py" in lesson for lesson in lessons)


def test_next_lesson_number_next_after_existing(
    test_domain_config: DomainConfig,
) -> None:
    """next_lesson_number should return one past the highest existing lesson."""
    num = next_lesson_number(test_domain_config)
    assert num == 3  # 001 and 002 exist


def test_next_lesson_number_override_target_dir(
    tmp_path: pathlib.Path,
) -> None:
    """target_dir override should scan the override dir, not config."""
    override = tmp_path / "custom"
    override.mkdir()
    (override / "001_a.py").write_text("# a", encoding="utf-8")
    (override / "005_b.py").write_text("# b", encoding="utf-8")
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    assert next_lesson_number(config, target_dir=override) == 6


def test_next_lesson_number_starts_at_one_when_empty(
    tmp_path: pathlib.Path,
) -> None:
    """next_lesson_number should return 1 when no lessons exist."""
    src = tmp_path / "src"
    src.mkdir()
    config = DomainConfig(
        name="empty",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=tmp_path,
        lesson_dir="src",
    )
    assert next_lesson_number(config) == 1


def test_validate_in_temp_valid_code() -> None:
    """validate_in_temp should run all validation tools on valid code."""
    code = (
        '"""Valid module."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def main() -> None:\n"
        '    """Run."""\n'
        '    print("hello")\n'
    )
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        strict_mypy=False,
    )
    result = validate_in_temp(code, config)
    assert result.is_valid
    assert "compile" in result.tools_run
    assert "ruff_format" in result.tools_run
    assert "ruff" in result.tools_run
    assert "mypy" in result.tools_run
    assert "pytest" in result.tools_run


def test_validate_in_temp_syntax_error() -> None:
    """validate_in_temp should detect syntax errors."""
    code = "def broken(\n"
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    result = validate_in_temp(code, config)
    assert not result.is_valid
    assert any("Syntax" in e for e in result.errors)


def test_validate_in_temp_normalizes_formatting() -> None:
    """validate_in_temp should auto-format code and return normalized_code."""
    # Extra blank lines that ruff format will remove
    code = (
        '"""Valid module."""\n\n'
        "from __future__ import annotations\n\n\n\n\n"
        "def main() -> None:\n"
        '    """Run."""\n'
        '    print("hello")\n'
    )
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        strict_mypy=False,
    )
    result = validate_in_temp(code, config)
    assert result.is_valid
    assert result.normalized_code is not None
    assert result.normalized_code != code


def test_validate_in_temp_no_normalize_when_already_formatted() -> None:
    """validate_in_temp should not set normalized_code when code is clean."""
    code = (
        '"""Valid module."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def main() -> None:\n"
        '    """Run."""\n'
        '    print("hello")\n'
    )
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        strict_mypy=False,
    )
    result = validate_in_temp(code, config)
    assert result.is_valid
    assert result.normalized_code is None


def test_validate_in_temp_failing_doctest() -> None:
    """validate_in_temp should detect failing doctests."""
    code = (
        '"""Module with bad doctest."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def add(a: int, b: int) -> int:\n"
        '    """Add two numbers.\n\n'
        "    Examples\n"
        "    --------\n"
        "    >>> add(1, 2)\n"
        "    999\n"
        '    """\n'
        "    return a + b\n"
    )
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        strict_mypy=False,
    )
    result = validate_in_temp(code, config)
    assert not result.is_valid
    assert "pytest" in result.tools_run
    assert any("pytest" in e for e in result.errors)


def test_validate_in_temp_skips_doctest_when_configured() -> None:
    """validate_in_temp should skip pytest when doctest_strategy='skip'."""
    code = (
        '"""Valid module."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def main() -> None:\n"
        '    """Run."""\n'
        '    print("hello")\n'
    )
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        strict_mypy=False,
        doctest_strategy="skip",
    )
    result = validate_in_temp(code, config)
    assert result.is_valid
    assert "pytest" not in result.tools_run


def test_write_lesson_creates_file(tmp_path: pathlib.Path) -> None:
    """write_lesson should create the file with the given content."""
    path = tmp_path / "output" / "001_test.py"
    write_lesson(path, "# test content")
    assert path.read_text() == "# test content"


def test_write_lesson_creates_parent_dirs(tmp_path: pathlib.Path) -> None:
    """write_lesson should create intermediate directories as needed."""
    path = tmp_path / "deep" / "nested" / "001_test.py"
    write_lesson(path, "# test")
    assert path.exists()


def test_write_lesson_overwrite_protection(tmp_path: pathlib.Path) -> None:
    """write_lesson should raise FileExistsError without --force."""
    path = tmp_path / "001_test.py"
    path.write_text("original")
    with pytest.raises(FileExistsError, match="Use --force"):
        write_lesson(path, "overwrite")


def test_write_lesson_force_overwrite(tmp_path: pathlib.Path) -> None:
    """write_lesson with force=True should overwrite existing files."""
    path = tmp_path / "001_test.py"
    path.write_text("original")
    write_lesson(path, "new content", force=True)
    assert path.read_text() == "new content"
