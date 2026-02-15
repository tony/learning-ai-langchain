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


class TestReadTemplate:
    """Tests for read_template."""

    def test_reads_project_template(
        self,
        test_domain_config: DomainConfig,
    ) -> None:
        result = read_template(test_domain_config)
        assert "Template" in result

    def test_fallback_when_no_project(self) -> None:
        config = DomainConfig(
            name="noproject",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
        )
        result = read_template(config)
        assert "demonstrate_concept" in result

    def test_fallback_when_template_missing(self, tmp_path: pathlib.Path) -> None:
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


class TestListExistingLessons:
    """Tests for list_existing_lessons."""

    def test_lists_py_files(self, test_domain_config: DomainConfig) -> None:
        lessons = list_existing_lessons(test_domain_config)
        assert "001_intro.py" in lessons
        assert "002_basics.py" in lessons

    def test_excludes_init(self, test_domain_config: DomainConfig) -> None:
        lessons = list_existing_lessons(test_domain_config)
        assert "__init__.py" not in lessons

    def test_empty_when_no_project(self) -> None:
        config = DomainConfig(
            name="none",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
        )
        assert list_existing_lessons(config) == []

    def test_handles_nested_dirs(self, tmp_path: pathlib.Path) -> None:
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


class TestNextLessonNumber:
    """Tests for next_lesson_number."""

    def test_next_after_existing(self, test_domain_config: DomainConfig) -> None:
        num = next_lesson_number(test_domain_config)
        assert num == 3  # 001 and 002 exist

    def test_override_target_dir(self, tmp_path: pathlib.Path) -> None:
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

    def test_starts_at_one_when_empty(self, tmp_path: pathlib.Path) -> None:
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


class TestValidateInTemp:
    """Tests for validate_in_temp."""

    def test_valid_code(self) -> None:
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
        assert "compile" in result.tools_run

    def test_syntax_error(self) -> None:
        code = "def broken(\n"
        config = DomainConfig(
            name="test",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
        )
        result = validate_in_temp(code, config)
        assert not result.is_valid
        assert any("Syntax" in e for e in result.errors)


class TestWriteLesson:
    """Tests for write_lesson."""

    def test_creates_file(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "output" / "001_test.py"
        write_lesson(path, "# test content")
        assert path.read_text() == "# test content"

    def test_creates_parent_dirs(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "deep" / "nested" / "001_test.py"
        write_lesson(path, "# test")
        assert path.exists()

    def test_overwrite_protection(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "001_test.py"
        path.write_text("original")
        with pytest.raises(FileExistsError, match="Use --force"):
            write_lesson(path, "overwrite")

    def test_force_overwrite(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "001_test.py"
        path.write_text("original")
        write_lesson(path, "new content", force=True)
        assert path.read_text() == "new content"
