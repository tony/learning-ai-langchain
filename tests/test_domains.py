"""Tests for lesson_generator.domains — registry and environment checks."""

from __future__ import annotations

import pathlib

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
def _clean_registry() -> None:
    """Snapshot and restore the registry around each test."""
    original = dict(_REGISTRY)
    yield  # type: ignore[misc]
    _REGISTRY.clear()
    _REGISTRY.update(original)


@pytest.mark.usefixtures("_clean_registry")
class TestGetDomain:
    """Tests for get_domain."""

    def test_returns_registered(self) -> None:
        config = DomainConfig(
            name="_test_reg",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
        )
        _register(config)
        assert get_domain("_test_reg") is config

    def test_raises_for_unknown(self) -> None:
        with pytest.raises(KeyError, match="Unknown domain"):
            get_domain("nonexistent_domain_xyz")


@pytest.mark.usefixtures("_clean_registry")
class TestListDomains:
    """Tests for list_domains."""

    def test_returns_sorted(self) -> None:
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


class TestValidateEnvironment:
    """Tests for validate_environment."""

    def test_ok_when_path_exists(self, tmp_path: pathlib.Path) -> None:
        config = DomainConfig(
            name="test",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
            project_path=tmp_path,
        )
        ok, msg = validate_environment(config)
        assert ok
        assert msg == "OK"

    def test_ok_when_no_path(self) -> None:
        config = DomainConfig(
            name="test",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
        )
        ok, _ = validate_environment(config)
        assert ok

    def test_fails_when_path_missing(self) -> None:
        config = DomainConfig(
            name="test",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
            project_path=pathlib.Path("/nonexistent/path/xyz"),
        )
        ok, msg = validate_environment(config)
        assert not ok
        assert "not found" in msg
