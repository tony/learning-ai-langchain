"""LangGraph state definition for the lesson generation pipeline."""

from __future__ import annotations

import typing as t

from pydantic import BaseModel, Field

#: Valid domain identifiers — must match keys in ``domains._REGISTRY``.
DomainName = t.Literal["dsa", "asyncio"]


class LessonGeneratorInput(BaseModel):
    """Input schema for the lesson generation graph.

    Defines the fields that callers (CLI, Studio UI) must or may provide
    when invoking the graph.  Uses Pydantic ``BaseModel`` so that
    LangGraph Studio renders descriptions and enum dropdowns.
    """

    topic: str = Field(
        description="Lesson topic, e.g. 'hash tables'",
    )
    domain_name: DomainName = Field(
        description="Learning domain to generate a lesson for",
    )
    target_dir: str | None = Field(
        default=None,
        description="Output directory (defaults to domain project)",
    )
    max_iterations: int = Field(
        default=3,
        description="Max generation/fix retry attempts",
    )
    dry_run: bool = Field(
        default=False,
        description="Validate only, don't write to disk",
    )
    force: bool = Field(
        default=False,
        description="Overwrite existing lesson files",
    )


class LessonGeneratorState(t.TypedDict, total=False):
    """State flowing through the lesson generation graph.

    Attributes
    ----------
    topic : str
        The lesson topic to generate content for.
    domain_name : str
        Name of the domain (e.g. ``"dsa"``, ``"asyncio"``).
    target_dir : str
        Directory where the generated lesson will be written (string for
        JSON serialization safety).
    template_content : str
        Content of the lesson template for this domain.
    existing_lessons : list[str]
        Filenames of existing lessons in the target directory.
    rendered_code : str
        The generated Python lesson code.
    metadata_json : str
        JSON-serialized :class:`~lesson_generator.models.LessonMetadata`.
    validation_ok : bool
        Whether the generated code passed all validation checks.
    validation_errors : list[str]
        Error messages from validation failures.
    iteration : int
        Current retry iteration (starts at 0).
    max_iterations : int
        Maximum number of generation/fix attempts.
    dry_run : bool
        If ``True``, skip writing output to disk.
    force : bool
        If ``True``, overwrite existing output files.
    output_path : str
        Final filesystem path of the written lesson.
    status : str
        Pipeline status: ``"pending"``, ``"generated"``, ``"validated"``,
        ``"committed"``, or ``"failed"``.
    """

    topic: str
    domain_name: str
    target_dir: str
    template_content: str
    existing_lessons: list[str]
    rendered_code: str
    metadata_json: str
    validation_ok: bool
    validation_errors: list[str]
    iteration: int
    max_iterations: int
    dry_run: bool
    force: bool
    output_path: str
    status: str
