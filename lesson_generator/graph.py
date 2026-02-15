"""LangGraph state graph construction for lesson generation."""

from __future__ import annotations

import typing as t

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from lesson_generator.nodes import (
    load_context,
    make_fix_node,
    make_generate_node,
    validate_lesson,
    write_output,
)
from lesson_generator.state import LessonGeneratorInput, LessonGeneratorState

_RetryRoute = t.Literal["write_output", "fix_lesson"]


def _should_retry(state: LessonGeneratorState) -> _RetryRoute:
    """Route after validation: retry, or write output.

    Parameters
    ----------
    state : LessonGeneratorState
        Current pipeline state.

    Returns
    -------
    Literal["write_output", "fix_lesson"]
        Next node name.
    """
    if state.get("validation_ok"):
        return "write_output"
    if state.get("iteration", 0) >= state.get("max_iterations", 3):
        return "write_output"
    return "fix_lesson"


def _build_graph(
    model: BaseChatModel,
) -> CompiledStateGraph:  # type: ignore[type-arg]
    """Compile the lesson generation pipeline with the given model.

    Parameters
    ----------
    model : BaseChatModel
        LLM to use for generation and fixing.

    Returns
    -------
    CompiledStateGraph
        Compiled LangGraph ready for invocation.
    """
    generate_lesson = make_generate_node(model)
    fix_lesson = make_fix_node(model)

    graph = StateGraph(LessonGeneratorState, input_schema=LessonGeneratorInput)
    graph.add_node("load_context", load_context)
    graph.add_node("generate_lesson", generate_lesson)  # type: ignore[arg-type]
    graph.add_node("validate_lesson", validate_lesson)
    graph.add_node("fix_lesson", fix_lesson)  # type: ignore[arg-type]
    graph.add_node("write_output", write_output)

    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "generate_lesson")
    graph.add_edge("generate_lesson", "validate_lesson")
    graph.add_conditional_edges("validate_lesson", _should_retry)
    graph.add_edge("fix_lesson", "validate_lesson")
    graph.add_edge("write_output", END)

    return graph.compile()


def create_lesson_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Zero-arg factory for ``langgraph.json``.

    The LangGraph dev server classifies factory functions by parameter
    count: a 1-param factory receives the runtime ``config`` dict as its
    first argument, which would shadow a ``model`` parameter.  This
    wrapper takes no arguments so the server calls it cleanly.

    Returns
    -------
    CompiledStateGraph
        Compiled LangGraph ready for invocation.
    """
    model = ChatAnthropic(model="claude-sonnet-4-5")  # type: ignore[call-arg]
    return _build_graph(model)
