"""Tests for lesson_generator.domains — registry and environment checks."""

from __future__ import annotations

import pathlib
from collections.abc import Iterator

import pytest

from lesson_generator.domains import (
    _REGISTRY,
    _register,
    get_domain,
    list_domains,
    validate_environment,
)
from lesson_generator.models import DomainConfig, PedagogyStyle, ProjectType


@pytest.fixture()
def _clean_registry() -> Iterator[None]:
    """Snapshot and restore the registry around each test."""
    original = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(original)


@pytest.mark.usefixtures("_clean_registry")
def test_get_domain_returns_registered() -> None:
    """get_domain should return a previously registered config."""
    config = DomainConfig(
        name="_test_reg",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    _register(config)
    assert get_domain("_test_reg") is config


@pytest.mark.usefixtures("_clean_registry")
def test_get_domain_raises_for_unknown() -> None:
    """get_domain should raise KeyError for unregistered domains."""
    with pytest.raises(KeyError, match="Unknown domain"):
        get_domain("nonexistent_domain_xyz")


@pytest.mark.usefixtures("_clean_registry")
def test_list_domains_returns_sorted() -> None:
    """list_domains should return domain names in sorted order."""
    for name in ("zzz", "aaa", "mmm"):
        _register(
            DomainConfig(
                name=name,
                pedagogy=PedagogyStyle.CONCEPT_FIRST,
                project_type=ProjectType.LESSON_BASED,
            ),
        )
    names = list_domains()
    assert "aaa" in names
    assert names == sorted(names)


def test_validate_environment_ok_when_path_exists(tmp_path: pathlib.Path) -> None:
    """validate_environment should pass when project_path exists."""
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=tmp_path,
    )
    ok, msg = validate_environment(config)
    assert ok
    assert msg == "OK"


def test_validate_environment_ok_when_no_path() -> None:
    """validate_environment should pass when no project_path is set."""
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
    )
    ok, _ = validate_environment(config)
    assert ok


def test_validate_environment_fails_when_path_missing() -> None:
    """validate_environment should fail when project_path doesn't exist."""
    config = DomainConfig(
        name="test",
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        project_type=ProjectType.LESSON_BASED,
        project_path=pathlib.Path("/nonexistent/path/xyz"),
    )
    ok, msg = validate_environment(config)
    assert not ok
    assert "not found" in msg
