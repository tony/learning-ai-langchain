"""LangGraph state definition for the lesson generation pipeline."""

from __future__ import annotations

import typing as t

from pydantic import Field


class LessonGeneratorInput(t.TypedDict, total=False):
    """Input schema for the lesson generation graph.

    Defines the fields that callers (CLI, Studio UI) must or may provide
    when invoking the graph.
    """

    topic: t.Required[
        t.Annotated[
            str,
            Field(
                description="Lesson topic, e.g. 'hash tables'",
            ),
        ]
    ]
    domain_name: t.Required[
        t.Annotated[
            str,
            Field(description="Domain: 'dsa' or 'asyncio'"),
        ]
    ]
    target_dir: t.Annotated[
        str,
        Field(description="Output directory (defaults to domain project)"),
    ]
    max_iterations: t.Annotated[
        int,
        Field(description="Max retry attempts (default: 3)"),
    ]
    dry_run: t.Annotated[
        bool,
        Field(description="Validate only, don't write to disk"),
    ]
    force: t.Annotated[
        bool,
        Field(description="Overwrite existing lesson files"),
    ]


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
