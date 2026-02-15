"""Run the ReAct agent from the command line."""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from .agent import create_react_graph

DEFAULT_QUERY = "What is the weather in SF?"


def main() -> None:
    """Run the agent with a user query."""
    load_dotenv()

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_QUERY

    graph = create_react_graph()
    result = graph.invoke(
        {"messages": [{"role": "user", "content": query}]},
    )

    for message in result["messages"]:
        if hasattr(message, "content") and message.content:
            print(f"{message.type}: {message.content}")


main()
