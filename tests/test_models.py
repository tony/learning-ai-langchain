"""Tests for lesson_generator.models — pure data, no LLM or filesystem."""

from __future__ import annotations

import pathlib

from lesson_generator.models import (
    DomainConfig,
    LessonMetadata,
    PedagogyStyle,
    ProjectType,
    ValidationResult,
)


def test_pedagogy_style_values() -> None:
    """PedagogyStyle enum should expose expected string values."""
    assert PedagogyStyle.CONCEPT_FIRST.value == "concept_first"
    assert PedagogyStyle.INTEGRATION_FIRST.value == "integration_first"
    assert PedagogyStyle.APPLICATION_FIRST.value == "application_first"


def test_pedagogy_style_str_mixin() -> None:
    """PedagogyStyle should have a useful str representation."""
    assert str(PedagogyStyle.CONCEPT_FIRST) == "PedagogyStyle.CONCEPT_FIRST"


def test_project_type_values() -> None:
    """ProjectType enum should expose expected string values."""
    assert ProjectType.LESSON_BASED.value == "lesson_based"
    assert ProjectType.APP_BASED.value == "app_based"


def test_domain_config_minimal() -> None:
    """DomainConfig with only required fields should use sensible defaults."""
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    assert config.name == "test"
    assert config.project_path is None
    assert config.lesson_dir == "src/"
    assert config.strict_mypy is True
    assert config.source_refs == {}


def test_domain_config_full(tmp_path: pathlib.Path) -> None:
    """DomainConfig with all fields should store them correctly."""
    config = DomainConfig(
        name="dsa",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=tmp_path,
        lesson_dir="src/algorithms",
        template_path="notes/template.py",
        source_refs={"cpython": "/study/c/cpython"},
        strict_mypy=True,
        doctest_strategy="deterministic",
    )
    assert config.project_path == tmp_path
    assert config.source_refs["cpython"] == "/study/c/cpython"


def test_lesson_metadata_minimal() -> None:
    """LessonMetadata with only required fields should default optional ones."""
    meta = LessonMetadata(number=1, title="Intro", filename="001_intro.py")
    assert meta.prerequisites == []
    assert meta.narrative == ""


def test_lesson_metadata_full() -> None:
    """LessonMetadata with all fields should store them correctly."""
    meta = LessonMetadata(
        number=3,
        title="Hash Tables",
        filename="003_hash_tables.py",
        prerequisites=["001_intro", "002_arrays"],
        narrative="Building on arrays...",
    )
    assert len(meta.prerequisites) == 2
    assert meta.narrative.startswith("Building")


def test_lesson_metadata_json_roundtrip() -> None:
    """LessonMetadata should survive JSON serialization round-trip."""
    meta = LessonMetadata(number=1, title="Test", filename="001_test.py")
    json_str = meta.model_dump_json()
    restored = LessonMetadata.model_validate_json(json_str)
    assert restored == meta


def test_validation_result_valid() -> None:
    """ValidationResult for valid code should have no errors."""
    result = ValidationResult(
        is_valid=True,
        tools_run=["compile", "ruff", "mypy"],
    )
    assert result.is_valid
    assert result.errors == []


def test_validation_result_invalid() -> None:
    """ValidationResult for invalid code should carry error messages."""
    result = ValidationResult(
        is_valid=False,
        errors=["ruff: E302 expected 2 blank lines"],
        tools_run=["compile", "ruff"],
    )
    assert not result.is_valid
    assert len(result.errors) == 1
