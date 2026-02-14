"""Agent definition for the ReAct agent."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
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
) -> create_react_agent:  # type: ignore[type-arg]
    """Create a ReAct agent with the given model.

    Parameters
    ----------
    model : BaseChatModel | None
        The chat model to use. Defaults to ChatAnthropic with claude-sonnet-4-20250514.

    Returns
    -------
    CompiledGraph
        A compiled LangGraph agent.
    """
    if model is None:
        model = ChatAnthropic(model="claude-sonnet-4-20250514")
    return create_react_agent(model, [search])


graph = create_agent()
