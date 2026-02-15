"""Data models for the lesson generation system."""

from __future__ import annotations

import enum
import pathlib

from pydantic import BaseModel, Field


class PedagogyStyle(enum.StrEnum):
    """Teaching approach for content generation.

    Each style maps to a different lesson structure and emphasis.
    """

    CONCEPT_FIRST = "concept_first"
    """DSA, asyncio: heavy doctests, pure Python, algorithmic focus."""

    INTEGRATION_FIRST = "integration_first"
    """LangChain, LangGraph, ADK: framework integration patterns."""

    APPLICATION_FIRST = "application_first"
    """Litestar, FastAPI: functioning server/app with tests."""


class ProjectType(enum.StrEnum):
    """Structure of the target learning project."""

    LESSON_BASED = "lesson_based"
    """Numbered lesson files (NNN_topic.py) with doctests."""

    APP_BASED = "app_based"
    """Application structure (src/app/ + tests/)."""


class DomainConfig(BaseModel):
    """Configuration for a content generation domain.

    Parameters
    ----------
    name : str
        Domain identifier (e.g. ``"dsa"``, ``"asyncio"``).
    pedagogy : PedagogyStyle
        Teaching approach to use.
    project_type : ProjectType
        Target project structure.
    project_path : pathlib.Path | None
        Path to the target learning project, if it exists on disk.
    lesson_dir : str
        Subdirectory within the project for lessons.
    template_path : str | None
        Relative path to a lesson template within the project.
    source_refs : dict[str, str]
        Mapping of reference names to paths for source material.
    strict_mypy : bool
        Whether to run mypy in strict mode for validation.
    doctest_strategy : str
        How to handle doctests: ``"deterministic"``, ``"ellipsis"``,
        or ``"skip"``.
    """

    name: str
    pedagogy: PedagogyStyle
    project_type: ProjectType
    project_path: pathlib.Path | None = None
    lesson_dir: str = "src/"
    template_path: str | None = None
    source_refs: dict[str, str] = Field(default_factory=dict)
    strict_mypy: bool = True
    doctest_strategy: str = "deterministic"


class LessonMetadata(BaseModel):
    """Metadata for a generated lesson.

    Parameters
    ----------
    number : int
        Lesson sequence number.
    title : str
        Human-readable lesson title.
    filename : str
        Output filename (e.g. ``"003_hash_tables.py"``).
    prerequisites : list[str]
        List of prerequisite lesson names.
    narrative : str
        Brief narrative context for the lesson.
    """

    number: int
    title: str
    filename: str
    prerequisites: list[str] = Field(default_factory=list)
    narrative: str = ""


class ValidationResult(BaseModel):
    """Result of running quality checks on generated code.

    Parameters
    ----------
    is_valid : bool
        Whether all checks passed.
    errors : list[str]
        Error messages from failed checks.
    tools_run : list[str]
        Names of validation tools that were executed.
    """

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    tools_run: list[str] = Field(default_factory=list)
