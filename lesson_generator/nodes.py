"""Graph node functions for the lesson generation pipeline.

Each function takes :class:`~lesson_generator.state.LessonGeneratorState`
and returns a partial state update dict.  The ``model``-dependent nodes
are created as closures inside :func:`make_generation_nodes`.
"""

from __future__ import annotations

import pathlib
import re
import typing as t
from collections.abc import Callable

from langchain_core.language_models import BaseChatModel

from lesson_generator.domains import get_domain
from lesson_generator.models import LessonMetadata
from lesson_generator.prompts import FIX_LESSON_PROMPT, GENERATE_LESSON_PROMPT
from lesson_generator.state import LessonGeneratorState
from lesson_generator.tools import (
    list_existing_lessons,
    next_lesson_number,
    read_template,
    validate_in_temp,
    write_lesson,
)

# Compiled regexes for stripping markdown code fences from LLM output.
# Both must match for stripping to occur — prevents false positives from
# backticks inside docstrings or inline code.
_OPENING_FENCE_RE = re.compile(r"^`{3,}[^\S\n]*\w*[^\S\n]*\n", re.ASCII)
_CLOSING_FENCE_RE = re.compile(r"\n[^\S\n]*`{3,}[^\S\n]*$", re.ASCII)


def _strip_code_fences(text: str) -> str:
    """Remove wrapping markdown code fences from LLM output.

    Only strips when both an opening fence (e.g. `` ```python ``) at the start
    and a closing fence (`` ``` ``) at the end are present.  Backticks embedded
    inside the code body (docstrings, inline reST) are left untouched.

    Parameters
    ----------
    text : str
        Raw LLM output, possibly wrapped in fences.

    Returns
    -------
    str
        Code with outer fences removed (if matched) and whitespace trimmed.
    """
    stripped = text.strip()
    if _OPENING_FENCE_RE.search(stripped) and _CLOSING_FENCE_RE.search(stripped):
        stripped = _OPENING_FENCE_RE.sub("", stripped, count=1)
        stripped = _CLOSING_FENCE_RE.sub("", stripped, count=1)
    return stripped.strip()


def load_context(state: LessonGeneratorState) -> dict[str, t.Any]:
    """Load template and existing lessons for the domain.

    Parameters
    ----------
    state : LessonGeneratorState
        Current pipeline state.

    Returns
    -------
    dict[str, Any]
        State updates: ``template_content``, ``existing_lessons``,
        ``iteration``, ``status``.
    """
    config = get_domain(state["domain_name"])
    template = read_template(config)
    target_dir = state.get("target_dir")
    override = pathlib.Path(target_dir) if target_dir is not None else None
    existing = list_existing_lessons(config, target_dir=override)
    return {
        "template_content": template,
        "existing_lessons": existing,
        "iteration": 0,
        "status": "pending",
    }


def make_generate_node(
    model: BaseChatModel,
) -> Callable[[LessonGeneratorState], dict[str, t.Any]]:
    """Create the ``generate_lesson`` node bound to a specific model.

    Parameters
    ----------
    model : BaseChatModel
        Language model for content generation.

    Returns
    -------
    Callable
        A graph node function.
    """

    def generate_lesson(state: LessonGeneratorState) -> dict[str, t.Any]:
        """Generate a Python lesson using the LLM."""
        config = get_domain(state["domain_name"])
        target_dir = state.get("target_dir")
        override = pathlib.Path(target_dir) if target_dir is not None else None
        number = next_lesson_number(config, target_dir=override)
        safe_topic = re.sub(r"[^a-z0-9_]", "_", state["topic"].lower())
        safe_topic = re.sub(r"_+", "_", safe_topic).strip("_")
        filename = f"{number:03d}_{safe_topic}.py"
        existing_str = "\n".join(state.get("existing_lessons", [])) or "(none)"

        chain = GENERATE_LESSON_PROMPT | model
        result = chain.invoke(
            {
                "template": state.get("template_content", ""),
                "existing_lessons": existing_str,
                "number": number,
                "filename": filename,
                "topic": state["topic"],
                "domain_name": state["domain_name"],
            },
        )
        code = _strip_code_fences(str(result.content))

        # Build metadata
        metadata = LessonMetadata(
            number=number,
            title=state["topic"],
            filename=filename,
        )

        return {
            "rendered_code": code,
            "metadata_json": metadata.model_dump_json(),
            "status": "generated",
        }

    return generate_lesson


def validate_lesson(state: LessonGeneratorState) -> dict[str, t.Any]:
    """Validate generated code in a temporary directory.

    Parameters
    ----------
    state : LessonGeneratorState
        Current pipeline state (must contain ``rendered_code``).

    Returns
    -------
    dict[str, Any]
        State updates: ``validation_ok``, ``validation_errors``.
    """
    config = get_domain(state["domain_name"])
    result = validate_in_temp(state["rendered_code"], config)
    return {
        "validation_ok": result.is_valid,
        "validation_errors": result.errors,
    }


def make_fix_node(
    model: BaseChatModel,
) -> Callable[[LessonGeneratorState], dict[str, t.Any]]:
    """Create the ``fix_lesson`` node bound to a specific model.

    Parameters
    ----------
    model : BaseChatModel
        Language model for fixing validation errors.

    Returns
    -------
    Callable
        A graph node function.
    """

    def fix_lesson(state: LessonGeneratorState) -> dict[str, t.Any]:
        """Ask the LLM to fix validation errors in the code."""
        errors_str = "\n".join(state.get("validation_errors", []))
        chain = FIX_LESSON_PROMPT | model
        result = chain.invoke(
            {
                "code": state["rendered_code"],
                "errors": errors_str,
            },
        )
        code = _strip_code_fences(str(result.content))
        iteration = state.get("iteration", 0) + 1
        return {
            "rendered_code": code,
            "iteration": iteration,
        }

    return fix_lesson


def write_output(state: LessonGeneratorState) -> dict[str, t.Any]:
    """Write the validated lesson to the target directory.

    Parameters
    ----------
    state : LessonGeneratorState
        Current pipeline state.

    Returns
    -------
    dict[str, Any]
        State updates: ``output_path``, ``status``.
    """
    if not state.get("validation_ok"):
        return {"status": "failed"}

    if state.get("dry_run"):
        return {"status": "dry_run"}

    metadata = LessonMetadata.model_validate_json(state["metadata_json"])
    raw_target = state.get("target_dir")
    if raw_target is not None:
        target_dir = pathlib.Path(raw_target).resolve()
    else:
        config = get_domain(state["domain_name"])
        if config.project_path is None:
            return {
                "status": "failed",
                "validation_errors": [
                    "No target_dir provided and domain has no project_path",
                ],
            }
        target_dir = (config.project_path / config.lesson_dir).resolve()
    target = (target_dir / metadata.filename).resolve()
    if not target.is_relative_to(target_dir):
        return {"status": "failed", "validation_errors": ["Path traversal detected"]}
    try:
        write_lesson(target, state["rendered_code"], force=state.get("force", False))
    except FileExistsError:
        return {"status": "failed", "validation_errors": [f"File exists: {target}"]}
    return {
        "output_path": str(target),
        "status": "committed",
    }
