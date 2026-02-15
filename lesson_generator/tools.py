"""Utility functions for lesson generation (file I/O, validation)."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

from lesson_generator.models import DomainConfig, ValidationResult
from lesson_generator.templates import get_builtin_template


def read_template(config: DomainConfig) -> str:
    """Read the lesson template for a domain.

    Tries the project-specific template first, falls back to
    the built-in template for the domain's pedagogy style.

    Parameters
    ----------
    config : DomainConfig
        Domain configuration.

    Returns
    -------
    str
        Template content.
    """
    if config.project_path and config.template_path:
        template_file = config.project_path / config.template_path
        if template_file.is_file():
            return template_file.read_text(encoding="utf-8")
    return get_builtin_template(config.pedagogy)


def list_existing_lessons(
    config: DomainConfig,
    *,
    target_dir: pathlib.Path | None = None,
) -> list[str]:
    """List existing lesson filenames in the domain's lesson directory.

    Parameters
    ----------
    config : DomainConfig
        Domain configuration with project path and lesson dir.
    target_dir : pathlib.Path | None
        Override directory to scan. When provided, this directory is
        used instead of ``config.project_path / config.lesson_dir``.

    Returns
    -------
    list[str]
        Sorted list of ``.py`` filenames (excluding ``__init__.py``
        and ``__pycache__``).
    """
    if target_dir is not None:
        lesson_dir = target_dir
    elif config.project_path is not None:
        lesson_dir = config.project_path / config.lesson_dir
    else:
        return []
    if not lesson_dir.is_dir():
        return []
    files: list[str] = []
    for p in sorted(lesson_dir.rglob("*.py")):
        if p.name.startswith("__"):
            continue
        # Store path relative to lesson_dir
        files.append(str(p.relative_to(lesson_dir)))
    return files


def next_lesson_number(
    config: DomainConfig,
    *,
    target_dir: pathlib.Path | None = None,
) -> int:
    """Determine the next lesson number from existing files.

    Scans filenames for a leading numeric prefix (e.g. ``003_topic.py``)
    and returns ``max + 1``. Returns ``1`` if no numbered lessons exist.

    Parameters
    ----------
    config : DomainConfig
        Domain configuration.
    target_dir : pathlib.Path | None
        Override directory to scan for existing lessons.

    Returns
    -------
    int
        Next available lesson number.
    """
    pattern = re.compile(r"^(\d+)")
    max_num = 0
    for filename in list_existing_lessons(config, target_dir=target_dir):
        # Use only the basename for matching
        basename = pathlib.PurePosixPath(filename).name
        m = pattern.match(basename)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num + 1


def validate_in_temp(code: str, config: DomainConfig) -> ValidationResult:
    """Validate generated code in a temporary directory.

    Runs the full quality pipeline: syntax check, ``ruff format``
    (normalization), ``ruff check``, ``mypy``, and ``pytest
    --doctest-modules``.  Normalized code (after ``ruff format``) is
    returned in :attr:`ValidationResult.normalized_code` when formatting
    changed the input.

    Parameters
    ----------
    code : str
        Python source code to validate.
    config : DomainConfig
        Domain configuration (controls mypy strictness and doctest
        strategy).

    Returns
    -------
    ValidationResult
        Validation outcome with errors, tools run, and optionally
        normalized code.
    """
    errors: list[str] = []
    tools_run: list[str] = []
    normalized_code: str | None = None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir) / "lesson.py"
        tmp_path.write_text(code, encoding="utf-8")

        # --- Syntax check via compile ---
        try:
            compile(code, str(tmp_path), "exec")
        except SyntaxError as exc:
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error: {exc}"],
                tools_run=["compile"],
            )
        tools_run.append("compile")

        # --- ruff format (normalization) ---
        try:
            subprocess.run(
                [sys.executable, "-m", "ruff", "format", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                is_valid=False,
                errors=["ruff format: timed out after 120s"],
                tools_run=[*tools_run, "ruff_format"],
            )
        tools_run.append("ruff_format")
        formatted = tmp_path.read_text(encoding="utf-8")
        if formatted != code:
            normalized_code = formatted

        # --- ruff check ---
        try:
            ruff_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                is_valid=False,
                errors=["ruff: timed out after 120s"],
                tools_run=[*tools_run, "ruff"],
                normalized_code=normalized_code,
            )
        tools_run.append("ruff")
        if ruff_result.returncode != 0:
            msg = ruff_result.stdout.strip()
            if ruff_result.stderr.strip():
                msg = f"{msg}\nstderr: {ruff_result.stderr.strip()}"
            errors.append(f"ruff: {msg}")

        # --- mypy ---
        if config.strict_mypy:
            mypy_args = [
                sys.executable,
                "-m",
                "mypy",
                "--strict",
                str(tmp_path),
            ]
        else:
            mypy_args = [sys.executable, "-m", "mypy", str(tmp_path)]

        try:
            mypy_result = subprocess.run(
                mypy_args,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                is_valid=False,
                errors=[*errors, "mypy: timed out after 120s"],
                tools_run=[*tools_run, "mypy"],
                normalized_code=normalized_code,
            )
        tools_run.append("mypy")
        if mypy_result.returncode != 0:
            msg = mypy_result.stdout.strip()
            if mypy_result.stderr.strip():
                msg = f"{msg}\nstderr: {mypy_result.stderr.strip()}"
            errors.append(f"mypy: {msg}")

        # --- pytest --doctest-modules ---
        if config.doctest_strategy != "skip":
            pytest_args = [
                sys.executable,
                "-m",
                "pytest",
                "--doctest-modules",
                str(tmp_path),
            ]
            if config.doctest_strategy == "ellipsis":
                pytest_args.extend(
                    [
                        "-o",
                        "doctest_optionflags=ELLIPSIS NORMALIZE_WHITESPACE",
                    ]
                )
            try:
                pytest_result = subprocess.run(
                    pytest_args,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired:
                return ValidationResult(
                    is_valid=False,
                    errors=[*errors, "pytest: timed out after 120s"],
                    tools_run=[*tools_run, "pytest"],
                    normalized_code=normalized_code,
                )
            tools_run.append("pytest")
            # Exit code 5 means "no tests collected" — not a failure.
            if pytest_result.returncode not in (0, 5):
                msg = pytest_result.stdout.strip()
                if pytest_result.stderr.strip():
                    msg = f"{msg}\nstderr: {pytest_result.stderr.strip()}"
                errors.append(f"pytest: {msg}")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        tools_run=tools_run,
        normalized_code=normalized_code,
    )


def write_lesson(
    path: pathlib.Path,
    content: str,
    *,
    force: bool = False,
) -> None:
    """Write lesson content to disk with overwrite protection.

    Creates parent directories as needed.

    Parameters
    ----------
    path : pathlib.Path
        Output file path.
    content : str
        Python source code to write.
    force : bool
        If ``True``, overwrite existing files.

    Raises
    ------
    FileExistsError
        If the file exists and ``force`` is ``False``.
    """
    if path.exists() and not force:
        msg = f"File already exists: {path}. Use --force to overwrite."
        raise FileExistsError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
