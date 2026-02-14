# AGENTS.md

This file provides guidance to AI agents (including Claude Code, Cursor, and other LLM-powered tools) when working with code in this repository.

## CRITICAL REQUIREMENTS

### Test Success
- ALL tests MUST pass for code to be considered complete and working
- Never describe code as "working as expected" if there are ANY failing tests
- Changes that break existing tests must be fixed before considering implementation complete
- A successful implementation must pass linting, type checking, AND all existing tests

## Project Overview

learning-ai-langchain is a minimal example project for [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph). It demonstrates a ReAct agent (`react_agent`) that uses tool-calling to answer questions.

Key features:
- Minimal ReAct agent using `langgraph.prebuilt.create_react_agent`
- Anthropic and OpenAI LLM support (Anthropic default)
- Local editable LangChain/LangGraph source via `[tool.uv.sources]`
- Follows conventions from the libtmux family of projects

## Development Environment

This project uses:
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [mypy](https://github.com/python/mypy) for type checking
- [pytest](https://docs.pytest.org/) for testing
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) for async test support

## Common Commands

### Setting Up Environment

```bash
uv sync
```

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

### Running the Agent

```bash
uv run python -m react_agent
```

With a custom query:

```bash
uv run python -m react_agent "What is the weather in SF?"
```

### Running Tests

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/test_agent.py
```

### Linting and Type Checking

Run ruff for linting:

```bash
uv run ruff check .
```

Format code with ruff:

```bash
uv run ruff format .
```

Run ruff linting with auto-fixes:

```bash
uv run ruff check . --fix --show-fixes
```

Run mypy for type checking:

```bash
uv run mypy react_agent
```

### Development Workflow

Follow this workflow for code changes:

1. **Format First**: `uv run ruff format .`
2. **Run Tests**: `uv run pytest`
3. **Run Linting**: `uv run ruff check . --fix --show-fixes`
4. **Check Types**: `uv run mypy react_agent`
5. **Verify Tests Again**: `uv run pytest`

## Code Architecture

```
react_agent/
  __init__.py      # Re-exports graph and create_agent
  agent.py         # Agent definition (create_agent, graph)
  __main__.py      # CLI runner for python -m react_agent
```

The agent is created via `create_react_agent` from `langgraph.prebuilt`, which implements a ReAct (Reason + Act) tool-calling loop.

## Coding Standards

### Imports

- **Use namespace imports for standard library modules**: `import enum` instead of `from enum import Enum`
  - **Exception**: `dataclasses` module may use `from dataclasses import dataclass, field` for cleaner decorator syntax
  - This rule applies to Python standard library only; third-party packages may use `from X import Y`
- **For typing**, use `import typing as t` and access via namespace: `t.NamedTuple`, etc.
- **Use `from __future__ import annotations`** at the top of all Python files

### Docstrings

Follow NumPy docstring style for all functions and methods:

```python
"""Short description of the function or class.

Detailed description using reStructuredText format.

Parameters
----------
param1 : type
    Description of param1
param2 : type
    Description of param2

Returns
-------
type
    Description of return value
"""
```

### Git Commit Standards

Format commit messages as:
```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.
what:
- Specific technical changes made
- Focused on a single topic
```

Common commit types:
- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev Dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (CLAUDE.md)

For multi-line commits, use heredoc to preserve formatting:
```bash
git commit -m "$(cat <<'EOF'
feat(Component[method]) add feature description

why: Explanation of the change.
what:
- First change
- Second change
EOF
)"
```

## Debugging Tips

When stuck in debugging loops:

1. **Pause and acknowledge the loop**
2. **Minimize to MVP**: Remove all debugging cruft and experimental code
3. **Document the issue** comprehensively for a fresh approach
4. **Format for portability** (using quadruple backticks)
