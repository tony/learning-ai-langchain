"""Tests for lesson_generator.graph — graph topology and mocked LLM paths."""

from __future__ import annotations

import pathlib
import typing as t

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from lesson_generator.domains import _register
from lesson_generator.graph import create_lesson_graph
from lesson_generator.models import DomainConfig, PedagogyStyle, ProjectType
from lesson_generator.state import LessonGeneratorState

VALID_LESSON = '''"""Test lesson."""

from __future__ import annotations


def demonstrate_concept() -> str:
    """Show concept.

    Examples
    --------
    >>> demonstrate_concept()
    'result'
    """
    return "result"


def main() -> None:
    """Run demo.

    Examples
    --------
    >>> main()
    result
    """
    print(demonstrate_concept())


if __name__ == "__main__":
    main()
'''


@pytest.fixture()
def _register_test_domain(tmp_path: pathlib.Path) -> t.Iterator[None]:
    """Register a temporary test domain and clean up after."""
    src = tmp_path / "src"
    src.mkdir()
    _register(
        DomainConfig(
            name="_test_graph",
            pedagogy=PedagogyStyle.CONCEPT_FIRST,
            project_type=ProjectType.LESSON_BASED,
            project_path=tmp_path,
            lesson_dir="src",
            strict_mypy=False,
        ),
    )
    yield
    # Clean up registry (the import caches it)
    from lesson_generator.domains import _REGISTRY

    _REGISTRY.pop("_test_graph", None)


@pytest.mark.usefixtures("_register_test_domain")
class TestLessonGraph:
    """Tests for the lesson generation graph."""

    def test_graph_compiles(self) -> None:
        """Graph should compile without errors."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        assert graph is not None

    def test_graph_has_expected_nodes(self) -> None:
        """Graph should contain all pipeline nodes."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        node_names = set(graph.get_graph().nodes)
        expected = {
            "load_context",
            "generate_lesson",
            "validate_lesson",
            "fix_lesson",
            "write_output",
            "__start__",
            "__end__",
        }
        assert expected == node_names

    def test_success_path(self, tmp_path: pathlib.Path) -> None:
        """Valid code should flow through to committed status."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        result = graph.invoke(
            {
                "topic": "test concept",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 3,
            },
        )
        assert result["status"] == "committed"
        assert pathlib.Path(result["output_path"]).exists()

    def test_dry_run_skips_write(self, tmp_path: pathlib.Path) -> None:
        """dry_run=True should skip writing and return status 'dry_run'."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        result = graph.invoke(
            {
                "topic": "test concept",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 3,
                "dry_run": True,
            },
        )
        assert result["status"] == "dry_run"
        # No file should have been written
        py_files = list(tmp_path.glob("*.py"))
        assert py_files == []

    def test_force_overwrites_existing(self, tmp_path: pathlib.Path) -> None:
        """force=True should overwrite an existing lesson file."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        # Create an existing file that will collide
        result = graph.invoke(
            {
                "topic": "test concept",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 3,
            },
        )
        assert result["status"] == "committed"
        existing_path = pathlib.Path(result["output_path"])
        assert existing_path.exists()

        # Re-run with force — should overwrite
        model2 = FakeListChatModel(responses=[VALID_LESSON])
        graph2 = create_lesson_graph(model=model2)
        result2 = graph2.invoke(
            {
                "topic": "test concept",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 3,
                "force": True,
            },
        )
        assert result2["status"] == "committed"

    def test_topic_sanitized_in_filename(self, tmp_path: pathlib.Path) -> None:
        """Topics with path traversal characters should be sanitized."""
        model = FakeListChatModel(responses=[VALID_LESSON])
        graph = create_lesson_graph(model=model)
        result = graph.invoke(
            {
                "topic": "foo/../../../escape",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 3,
            },
        )
        assert result["status"] == "committed"
        output = pathlib.Path(result["output_path"])
        # File must be inside target_dir
        assert output.resolve().is_relative_to(tmp_path.resolve())
        # Filename must not contain path separators
        assert "/" not in output.name
        assert ".." not in output.name

    def test_file_exists_returns_failed(self, tmp_path: pathlib.Path) -> None:
        """FileExistsError in write_output should return status='failed'."""
        from lesson_generator.models import LessonMetadata
        from lesson_generator.nodes import write_output

        # Pre-create the collision file
        (tmp_path / "001_topic.py").write_text("# existing", encoding="utf-8")

        metadata = LessonMetadata(number=1, title="topic", filename="001_topic.py")
        state: LessonGeneratorState = {
            "validation_ok": True,
            "target_dir": str(tmp_path),
            "rendered_code": "# new content",
            "metadata_json": metadata.model_dump_json(),
        }
        result = write_output(state)
        assert result["status"] == "failed"

    def test_max_retries_respected(self, tmp_path: pathlib.Path) -> None:
        """After max retries, should stop retrying."""
        bad_code = "def broken( -> None:\n    pass"
        # Provide enough responses for generate + max_retries fixes
        responses = [bad_code] * 5
        model = FakeListChatModel(responses=responses)
        graph = create_lesson_graph(model=model)
        result = graph.invoke(
            {
                "topic": "broken",
                "domain_name": "_test_graph",
                "target_dir": str(tmp_path),
                "max_iterations": 2,
            },
        )
        assert result["status"] == "failed"
