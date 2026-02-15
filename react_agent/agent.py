"""Agent definition for the ReAct agent."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent


@tool
def search(query: str) -> str:
    """Search for information.

    Parameters
    ----------
    query : str
        The search query to look up.

    Returns
    -------
    str
        The search result.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def create_agent(
    model: BaseChatModel | None = None,
) -> CompiledStateGraph:  # type: ignore[type-arg]
    """Create a ReAct agent with the given model.

    Parameters
    ----------
    model : BaseChatModel | None
        The chat model to use. Defaults to ChatAnthropic with
        claude-sonnet-4-5.

    Returns
    -------
    CompiledStateGraph
        A compiled LangGraph agent.
    """
    if model is None:
        model = ChatAnthropic(model="claude-sonnet-4-5")  # type: ignore[call-arg]
    # NOTE: create_react_agent is deprecated in favor of langchain.agents.create_agent,
    # but the replacement is not yet available in the current environment.
    return create_react_agent(model, [search])


graph = create_agent()
