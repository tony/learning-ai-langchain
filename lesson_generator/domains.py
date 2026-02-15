"""Static domain registry for lesson generation."""

from __future__ import annotations

import os
import pathlib

from lesson_generator.models import DomainConfig, PedagogyStyle, ProjectType

_REGISTRY: dict[str, DomainConfig] = {}

# Default study root for resolving project paths
_STUDY_ROOT = pathlib.Path(
    os.environ.get("LESSON_STUDY_ROOT", str(pathlib.Path.home() / "study" / "python"))
)


def _register(config: DomainConfig) -> None:
    """Register a domain configuration."""
    _REGISTRY[config.name] = config


def get_domain(name: str) -> DomainConfig:
    """Look up a domain by name.

    Parameters
    ----------
    name : str
        Domain identifier.

    Returns
    -------
    DomainConfig
        The domain configuration.

    Raises
    ------
    KeyError
        If the domain is not registered.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        msg = f"Unknown domain {name!r}. Available: {available}"
        raise KeyError(msg)
    return _REGISTRY[name]


def list_domains() -> list[str]:
    """Return sorted list of registered domain names.

    Returns
    -------
    list[str]
        Available domain names.
    """
    return sorted(_REGISTRY)


def validate_environment(config: DomainConfig) -> tuple[bool, str]:
    """Check whether a domain's target project exists on disk.

    Parameters
    ----------
    config : DomainConfig
        Domain to validate.

    Returns
    -------
    tuple[bool, str]
        ``(ok, message)`` — ``True`` if project path exists or is
        unconfigured, ``False`` with an explanation otherwise.
    """
    if config.project_path is None:
        return True, "No project path configured; --out required."
    if not config.project_path.is_dir():
        return (
            False,
            f"Target project not found at {config.project_path}. "
            "Use --out to specify an explicit output path.",
        )
    return True, "OK"


# ---------------------------------------------------------------------------
# MVP domains
# ---------------------------------------------------------------------------

_register(
    DomainConfig(
        name="dsa",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=_STUDY_ROOT / "learning-dsa",
        lesson_dir="src/algorithms",
        template_path="notes/lesson_template.py",
        source_refs={
            "cpython": str(pathlib.Path.home() / "study" / "c" / "cpython"),
        },
        strict_mypy=True,
        doctest_strategy="deterministic",
    ),
)

_register(
    DomainConfig(
        name="asyncio",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=_STUDY_ROOT / "learning-asyncio",
        lesson_dir="src",
        template_path="notes/lesson_template.py",
        source_refs={
            "cpython": str(pathlib.Path.home() / "study" / "c" / "cpython"),
        },
        strict_mypy=True,
        doctest_strategy="ellipsis",
    ),
)
