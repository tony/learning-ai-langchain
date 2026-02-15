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


class TestPedagogyStyle:
    """Tests for the PedagogyStyle enum."""

    def test_values(self) -> None:
        assert PedagogyStyle.CONCEPT_FIRST.value == "concept_first"
        assert PedagogyStyle.INTEGRATION_FIRST.value == "integration_first"
        assert PedagogyStyle.APPLICATION_FIRST.value == "application_first"

    def test_str_mixin(self) -> None:
        assert str(PedagogyStyle.CONCEPT_FIRST) == "PedagogyStyle.CONCEPT_FIRST"


class TestProjectType:
    """Tests for the ProjectType enum."""

    def test_values(self) -> None:
        assert ProjectType.LESSON_BASED.value == "lesson_based"
        assert ProjectType.APP_BASED.value == "app_based"


class TestDomainConfig:
    """Tests for the DomainConfig model."""

    def test_minimal(self) -> None:
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

    def test_full(self, tmp_path: pathlib.Path) -> None:
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


class TestLessonMetadata:
    """Tests for the LessonMetadata model."""

    def test_minimal(self) -> None:
        meta = LessonMetadata(number=1, title="Intro", filename="001_intro.py")
        assert meta.prerequisites == []
        assert meta.narrative == ""

    def test_full(self) -> None:
        meta = LessonMetadata(
            number=3,
            title="Hash Tables",
            filename="003_hash_tables.py",
            prerequisites=["001_intro", "002_arrays"],
            narrative="Building on arrays...",
        )
        assert len(meta.prerequisites) == 2
        assert meta.narrative.startswith("Building")

    def test_json_roundtrip(self) -> None:
        meta = LessonMetadata(number=1, title="Test", filename="001_test.py")
        json_str = meta.model_dump_json()
        restored = LessonMetadata.model_validate_json(json_str)
        assert restored == meta


class TestValidationResult:
    """Tests for the ValidationResult model."""

    def test_valid(self) -> None:
        result = ValidationResult(
            is_valid=True,
            tools_run=["compile", "ruff", "mypy"],
        )
        assert result.is_valid
        assert result.errors == []

    def test_invalid(self) -> None:
        result = ValidationResult(
            is_valid=False,
            errors=["ruff: E302 expected 2 blank lines"],
            tools_run=["compile", "ruff"],
        )
        assert not result.is_valid
        assert len(result.errors) == 1
