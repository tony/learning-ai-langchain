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

Keep the subject ≤50 chars (excluding any trailing `(#NN)` PR ref); wrap
body lines at ≤72 chars. Separate the `why:` and `what:` blocks with a
blank line.

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

## Testing Strategy

### Testing Guidelines

1. **Use functional tests only**: Write tests as standalone functions (`test_*`), not classes. Avoid `class TestFoo:` groupings — use descriptive function names and file organization instead. This applies to pytest tests, not doctests.

2. **Use existing fixtures over mocks**
   - Use fixtures from `conftest.py` instead of `monkeypatch` and `MagicMock` when available
   - For lesson_generator, use provided fixtures: `sample_template`, `mock_project_dir`, `test_domain_config`
   - Document in test docstrings why standard fixtures weren't used for exceptional cases

3. **Preferred pytest patterns**
   - Use `tmp_path` (pathlib.Path) fixture over Python's `tempfile`
   - Use `monkeypatch` fixture over `unittest.mock`

### Parametrized Tests

Use `typing.NamedTuple` with a `test_id` field for parametrized test cases:

```python
class SomeFixture(t.NamedTuple):
    test_id: str
    input_value: str
    expected: str

SOME_FIXTURES: list[SomeFixture] = [
    SomeFixture(
        test_id="basic_case",
        input_value="hello",
        expected="HELLO",
    ),
    SomeFixture(
        test_id="empty_string",
        input_value="",
        expected="",
    ),
]

@pytest.mark.parametrize(
    list(SomeFixture._fields),
    SOME_FIXTURES,
    ids=[test.test_id for test in SOME_FIXTURES],
)
def test_transform(
    test_id: str,
    input_value: str,
    expected: str,
) -> None:
    """Transform should uppercase input."""
    assert transform(input_value) == expected
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures (sample_template, mock_project_dir, etc.)
├── test_domains.py      # Domain registry and validation
├── test_graph.py        # Graph topology and mocked LLM paths
├── test_models.py       # Pydantic model unit tests
└── test_tools.py        # Tool functions (read_template, validate_in_temp, etc.)
```

## LangGraph Dev Server

### Starting the Server

```bash
uv run langgraph dev --no-browser        # local only
uv run langgraph dev --tunnel --no-browser  # with cloudflare tunnel
```

The server runs on `http://localhost:2024`. Configuration is in `langgraph.json`:
- `lesson_generator` — `./lesson_generator/graph.py:create_lesson_graph`
- `react_agent` — `./react_agent/agent.py:create_react_graph`

### Checking if the Server is Running

```bash
curl -s http://localhost:2024/ok          # => {"ok":true}
curl -s http://localhost:2024/info | jq . # server version, flags, host info
```

### Querying the API with curl

All search/list endpoints use `POST` with a JSON body. Individual resource GETs use `GET`.

**List assistants (graphs):**
```bash
curl -s http://localhost:2024/assistants/search \
  -X POST -H 'Content-Type: application/json' -d '{}' | jq .
```

**Search threads:**
```bash
curl -s http://localhost:2024/threads/search \
  -X POST -H 'Content-Type: application/json' -d '{"limit": 5}' \
  | jq '[.[] | {thread_id, status, updated_at}]'
```

**List runs for a thread:**
```bash
curl -s http://localhost:2024/threads/{thread_id}/runs | jq .
```

**Get a specific run (runs are thread-scoped):**
```bash
curl -s http://localhost:2024/threads/{thread_id}/runs/{run_id} | jq .
```

**Get thread state (final values after a run):**
```bash
curl -s http://localhost:2024/threads/{thread_id}/state | jq .values
```

**Find a run by ID when you don't know the thread** — iterate threads:
```bash
for tid in $(curl -s http://localhost:2024/threads/search \
  -X POST -H 'Content-Type: application/json' -d '{"limit": 50}' \
  | jq -r '.[].thread_id'); do
  result=$(curl -s "http://localhost:2024/threads/$tid/runs/{run_id}")
  if echo "$result" | jq -e '.run_id' >/dev/null 2>&1; then
    echo "Thread: $tid"
    echo "$result" | jq .
    break
  fi
done
```

**Create a run (invoke a graph):**
```bash
curl -s http://localhost:2024/threads/{thread_id}/runs \
  -X POST -H 'Content-Type: application/json' \
  -d '{"assistant_id": "{assistant_id}", "input": {"topic": "example", "domain_name": "asyncio"}}'
```

### Key API Patterns

- Threads are created implicitly on first run, or explicitly via `POST /threads`
- Runs are always scoped to a thread: `/threads/{thread_id}/runs/{run_id}`
- A run with `"status": "success"` means the graph completed without crashing — check `thread/state` for the graph's own status (e.g., `"failed"` if validation failed after max retries)
- Search endpoints (`/threads/search`, `/assistants/search`) require `POST` with JSON body
- Info endpoints (`/ok`, `/info`) use `GET`

## Debugging Tips

When stuck in debugging loops:

1. **Pause and acknowledge the loop**
2. **Minimize to MVP**: Remove all debugging cruft and experimental code
3. **Document the issue** comprehensively for a fresh approach
4. **Format for portability** (using quadruple backticks)

## AI Slop Prevention

Treat AI slop as **review-hostile noise**, not as proof that text or
code is wrong. The goal is to maximize information density by removing
artifacts that make the repository harder to trust or navigate.

### The Anti-Slop Rubric

Before committing, audit all AI-assisted changes for these noise
patterns:

- **AI Signatures:** Remove "Generated by", footers, conversational
  filler ("Certainly!", "Here is..."), unexplained emojis (🤖, ✨), and
  AI-tool metadata.
- **Brittle References:** Avoid hard-coded line numbers, fragile
  file/test counts, dated "as of" claims, bare SHAs, and local
  absolute paths unless they are strict evidentiary artifacts (e.g.,
  benchmark logs).
- **Diff Narration:** Do not restate what moved, was renamed, or was
  removed in artifacts the downstream reader holds: code, docstrings,
  README, CHANGES, PR descriptions, or release notes. The diff and
  commit message already carry this history.
- **Branch-Internal Narrative:** Do not mention intermediate branch
  states, abandoned approaches, or "no longer" behavior unless users
  of a published release actually experienced the old state (**The
  Published-Release Test**).
- **Low-Value Scaffolding:** Remove ownerless TODOs (`TODO: revisit`),
  unused future-proofing, debug artifacts, and defensive wrappers that
  do not protect a currently reachable failure mode.
- **Prose Inflation:** Replace generic AI "tells" like *comprehensive,
  robust, seamless, production-ready, leverage, delve, tapestry,* and
  *best practices* with concrete descriptions of behavior,
  constraints, or trade-offs.
- **Coded Labels:** Write rules, options, and findings as plain
  imperatives. Don't tag them with codes like `[R1]`, `A1`, or
  `Option B` in artifacts a human reads — the reader shouldn't have to
  decode an index. Internal agent bookkeeping may use ids; shipped text
  may not.

### Durable Source Links

Link to a pinned revision, never to trunk. A pinned permalink is not a
brittle reference; an unlinked SHA dropped into prose is. `blob/main/…`
links rot silently — the file moves, lines shift, and the anchor lands
on unrelated code while still resolving.

- Prefer a release tag (`blob/v1.4.0/…`). Most durable, and it tells
  the reader which released version the claim held for.
- Otherwise use a 7-char commit ref (`blob/9a29b1a/…`) reachable from
  trunk. Use when there is no tag or the claim is about unreleased
  code. Never a PR-head SHA — it can be rebased or garbage-collected.
- Reserve `blob/main/…` for living documents meant to always show the
  latest state, such as a contributing guide.
- Line anchors (`#L120-L145`) are only safe on a pinned ref.

### Preservation & Context

**When unsure, leave the text in place and ask.** Subjective cleanup
must never be a reason to remove load-bearing rationale.

- **Preserve the "Why":** You MUST NOT delete comments that document
  invariants, protocol constraints, platform quirks, security
  boundaries, and upstream workarounds.
- **Evidence is Immune:** Preserve exact counts, dates, and SHAs when
  they serve as evidence in benchmark results, release notes, stack
  traces, or lockfiles.
- **Behavior Over Inventory:** A useful description explains what
  changed for the *system or user*; it does not provide an inventory
  of files or functions the diff already shows.

### Change Discipline

- Make the smallest coherent change that solves the verified problem;
  keep unrelated cleanup out of it.
- Reuse an existing file, component, helper, API, or test before adding
  a new one. Modify in place when the change fits the file's
  responsibility.
- Keep new APIs private until a caller outside the module needs them.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized high-touch module — not
  for a single-use helper or a one-line re-export.

### Keep Instructions Lean

Treat this file like code and prune it.

- Delete a line whose removal would not cause a mistake.
- Move multi-step procedures into skills, path-specific rules into
  nested AGENTS.md files, and hard limits into hooks or CI.
- Keep only non-obvious, broadly applicable defaults here. Anything a
  reader can infer from the code, a manifest, or a linter does not
  belong.

## Shipped vs. Branch-Internal Narrative

Long-running branches accumulate tactical decisions — renames,
refactors, attempts-then-reverts, intermediate states. Commit messages
and the diff hold *what changed* and *why*. Do not restate either in
artifacts the downstream reader holds: code, docstrings, README,
CHANGES, PR descriptions, release notes, migration guides.

When deciding what counts as branch-internal, use trunk or the parent
branch as the baseline — not intermediate states inside the current
branch.

**The Published-Release Test**

Before adding rename history, "previously" / "formerly" / "no longer
X" phrasing, "removed" / "moved" / "refactored" / "fixed" diff
paraphrases, or `### Fixes` entries to a user-facing surface, ask:

> Did users of the most recently published release ever experience
> this old name, old behavior, or bug?

If the answer is no, it is branch-internal narrative. Move it to the
commit message and describe only the current state in the artifact.

**Keep in shipped artifacts**

- Deprecations and migration guides for symbols that actually shipped.
- `### Fixes` entries for bugs that affected users of a published
  release.
- Comments explaining *why the current code looks this way* —
  invariants, platform quirks, upstream bug workarounds — that make
  sense to a reader who never saw the previous version.

**Default**: when in doubt, keep the artifact clean and put the story
in the commit.

### Cleanup in Hindsight

When applying this rule retroactively from inside a feature branch,
first establish scope by diffing against the parent branch (or trunk)
to identify which commits this branch actually introduced. Then:

- **Commits introduced in this branch** — prompt the user with two
  options: `fixup!` commits with `git rebase --autosquash` to address
  each causal commit at its source, or a single cleanup commit at
  branch tip. User chooses.
- **Commits already in trunk or a parent branch** — default to
  leaving them alone. Do not raise them as cleanup candidates; act
  only on explicit user instruction. If the user opts in, fold the
  cleanup into a single commit at branch tip and do not rewrite trunk
  or parent-branch history.
- **Scope guard** — if cleaning in-branch bleed would touch a
  colleague's in-flight work or expand the branch beyond its stated
  goal, default to staying in lane: protect the project's current
  goal, leave prior bleed alone, and don't introduce new bleed in the
  current change.
