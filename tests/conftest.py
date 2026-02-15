"""Shared fixtures for lesson_generator tests."""

from __future__ import annotations

import os
import pathlib

import pytest

from lesson_generator.models import DomainConfig, PedagogyStyle, ProjectType


@pytest.fixture()
def sample_template() -> str:
    """Return a minimal lesson template string."""
    return (
        "#!/usr/bin/env python\n"
        '"""Lesson {number}: {title}."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def main() -> None:\n"
        '    """Run demonstration."""\n'
        '    print("hello")\n\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n"
    )


@pytest.fixture()
def mock_project_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create a minimal project directory with a lesson template.

    Returns
    -------
    pathlib.Path
        Root of the mock project.
    """
    notes = tmp_path / "notes"
    notes.mkdir()
    template = notes / "lesson_template.py"
    template.write_text(
        "#!/usr/bin/env python\n"
        '"""Template."""\n\n'
        "from __future__ import annotations\n\n\n"
        "def main() -> None:\n"
        '    """Run demo."""\n'
        '    print("template")\n',
        encoding="utf-8",
    )

    # Create some existing lesson files
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "001_intro.py").write_text(
        '"""Intro lesson."""\n',
        encoding="utf-8",
    )
    (src / "002_basics.py").write_text(
        '"""Basics lesson."""\n',
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def test_domain_config(mock_project_dir: pathlib.Path) -> DomainConfig:
    """Return a DomainConfig pointing at the mock project."""
    return DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=mock_project_dir,
        lesson_dir="src",
        template_path="notes/lesson_template.py",
        strict_mypy=False,
    )


@pytest.fixture()
def api_keys_available() -> bool:
    """Check if real API keys are set."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
