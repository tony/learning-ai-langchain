"""Prompt templates for lesson generation and correction."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

GENERATE_LESSON_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert Python instructor creating learning content.\n\n"
            "CONVENTIONS (must follow):\n"
            "- Use `from __future__ import annotations` at the top\n"
            "- Use namespace imports for stdlib: `import typing as t`, "
            "`import pathlib`, etc.\n"
            "- Exception: `from dataclasses import dataclass, field` is OK\n"
            "- NumPy-style docstrings on all public functions\n"
            "- Type hints on all functions (mypy --strict compatible)\n"
            "- Include doctests in Examples sections\n"
            "- Ensure `pytest --doctest-modules` passes\n"
            "- Keep lessons self-contained and runnable\n"
            "- Include a `main()` function and `if __name__ == '__main__'` guard\n\n"
            "TEMPLATE (follow this structure):\n"
            "`````\n{template}\n`````\n\n"
            "EXISTING LESSONS in this project (avoid overlap):\n"
            "{existing_lessons}\n\n"
            "The lesson number is {number} and filename is {filename}.",
        ),
        (
            "human",
            "Generate a complete, self-contained Python lesson on: {topic}\n\n"
            "Domain: {domain_name}\n\n"
            "OUTPUT RULES:\n"
            "1. Return ONLY valid Python source code\n"
            "2. Do NOT wrap the output in markdown code fences "
            "(no ``` or ```python)\n"
            "3. The first line must be a Python docstring or comment",
        ),
    ],
)


FIX_LESSON_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are fixing a Python lesson that failed validation.\n\n"
            "CONVENTIONS (same as original):\n"
            "- `from __future__ import annotations` at the top\n"
            "- Namespace imports for stdlib\n"
            "- NumPy-style docstrings\n"
            "- Type hints (mypy --strict compatible)\n"
            "- Doctests must pass under `pytest --doctest-modules`\n",
        ),
        (
            "human",
            "The following code failed validation:\n\n"
            "`````python\n{code}\n`````\n\n"
            "Errors:\n{errors}\n\n"
            "OUTPUT RULES:\n"
            "1. Return ONLY valid Python source code\n"
            "2. Do NOT wrap the output in markdown code fences "
            "(no ``` or ```python)\n"
            "3. The first line must be a Python docstring or comment",
        ),
    ],
)
