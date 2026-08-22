# Contributing

Thanks for looking. This is a personal learning project for LangChain and
LangGraph; the most useful contribution is a bug report with a reproduction,
or a note on where a domain fails to produce a valid lesson.

How this project writes prose — README, commit messages, docstrings, and
source comments — is set out separately in [WRITING.md](WRITING.md). Read
that before changing any of it. The constraints every change is held to, and
the map of what is where, are in [AGENTS.md](../AGENTS.md).

## Getting set up

```console
$ uv sync
```

`[tool.uv.sources]` points `langchain-core`, `langchain-anthropic`,
`langchain-openai`, `langgraph`, `langgraph-prebuilt`, `langgraph-checkpoint`,
and `langgraph-sdk` at local editable checkouts under
`../../../study/ai-agents/` relative to this repository. `uv sync` fails if
those sibling checkouts are not present.

Copy the environment template and fill in real keys:

```console
$ cp .env.example .env
```

`ANTHROPIC_API_KEY` is required to run either agent for real; `OPENAI_API_KEY`
and `LANGSMITH_API_KEY` are optional. The test suite needs none of them — see
[Tests](#tests).

## The gates

Format:

```console
$ uv run ruff format .
```

Lint:

```console
$ uv run ruff check . --fix --show-fixes
```

Type-check:

```console
$ uv run mypy lesson_generator react_agent
```

Test:

```console
$ uv run pytest
```

Each has a `just` shortcut (`just fmt`, `just lint`, `just lint-fix`,
`just typecheck`, `just test`) in the `justfile`. There is no CI in this
repository, so the `justfile` — not a workflow — is the order of record: a
change is done when all four gates above pass locally.

No prompted example runs as part of `pytest`; see
[WRITING.md](WRITING.md#documented-examples-that-run) for why, and for the
separate mechanism `lesson_generator` uses to validate the doctests in code
it generates.

Before claiming a test or a gate works, show it failing. A gate that has
never been red is an assumption.

## Coding standards

`ruff`'s `required-imports` enforces `from __future__ import annotations` at
the top of every module.

Import style itself is a convention `ruff` does not check: prefer a
namespace import for the standard library (`import enum`, `import pathlib`)
over `from enum import Enum`. `from dataclasses import dataclass, field` is
the one accepted exception, and third-party imports use `from x import y`
freely. For `typing`, write `import typing as t` and reference members
through the namespace: `t.NamedTuple`, `t.Any`.

## Tests

The suite runs without any API key: `tests/test_graph.py` substitutes
`langchain_core`'s `FakeListChatModel` for a real model, so no network call
and no key are needed. `asyncio_mode = "auto"` in `pyproject.toml` means an
`async def test_*` needs no `@pytest.mark.asyncio`.

- **Use functional tests only.** Write tests as standalone `test_*`
  functions, not `class TestFoo:` groupings. This applies to pytest tests,
  not doctests.
- **Use the fixtures in `tests/conftest.py` before reaching for a mock.**
  `sample_template`, `mock_project_dir`, and `test_domain_config` build a
  throwaway project on `tmp_path`; `api_keys_available` checks for a real
  `ANTHROPIC_API_KEY` for the rare test that wants one. When a test skips
  these for a real exception, say why in its docstring.
- **Prefer `tmp_path` over `tempfile`, and `monkeypatch` over
  `unittest.mock`.**
- **Parametrize with `typing.NamedTuple`.** Give every case a `test_id`
  field and pass `ids=[c.test_id for c in CASES]` — see
  `tests/test_nodes.py::test_strip_code_fences` for the pattern.
- `--strict-markers` is set, so a new `@pytest.mark.foo` needs a matching
  entry in `pyproject.toml` before it will collect.

`tests/test_tools.py`'s `validate_in_temp` tests shell out to `ruff`, `mypy`,
and `pytest` as subprocesses (the same pipeline the tool runs on generated
lessons); those binaries come from this project's own `dev` dependency group,
so no extra setup is needed beyond `uv sync`.

## Running the LangGraph dev server

```console
$ uv run langgraph dev --no-browser
```

or, with a Cloudflare tunnel (`just studio`):

```console
$ uv run langgraph dev --tunnel --no-browser
```

The server runs on `http://localhost:2024`. `langgraph.json` registers two
graphs: `lesson_generator` (`./lesson_generator/graph.py:create_lesson_graph`)
and `react_agent` (`./react_agent/agent.py:create_react_graph`).

Check it is up:

```console
$ curl -s http://localhost:2024/ok
```

Get server info (version, flags, host):

```console
$ curl -s http://localhost:2024/info | jq .
```

Search and list endpoints take `POST` with a JSON body; single-resource
lookups take `GET`. A few examples:

List the registered graphs:

```console
$ curl -s http://localhost:2024/assistants/search \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{}' \
    | jq .
```

Search threads:

```console
$ curl -s http://localhost:2024/threads/search \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"limit": 5}' \
    | jq '[.[] | {thread_id, status, updated_at}]'
```

List a thread's runs:

```console
$ curl -s http://localhost:2024/threads/{thread_id}/runs | jq .
```

Get a specific run (runs are thread-scoped):

```console
$ curl -s http://localhost:2024/threads/{thread_id}/runs/{run_id} | jq .
```

Get a thread's final state:

```console
$ curl -s http://localhost:2024/threads/{thread_id}/state | jq .values
```

Create a run:

```console
$ curl -s http://localhost:2024/threads/{thread_id}/runs \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"assistant_id": "lesson_generator", "input": {"topic": "hash tables", "domain_name": "dsa"}}'
```

Find a run by ID without knowing its thread. Set the run ID first, then
search recent threads and check each one's runs for a match:

```console
$ run_id=<the-run-id-you-have>
```

```console
$ for tid in $(curl -s http://localhost:2024/threads/search \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"limit": 50}' \
    | jq -r '.[].thread_id'); do
    result=$(curl -s "http://localhost:2024/threads/$tid/runs/$run_id")
    if echo "$result" | jq -e '.run_id' >/dev/null 2>&1; then
      echo "Thread: $tid"
      echo "$result" | jq .
      break
    fi
  done
```

A run with `"status": "success"` only means the graph finished without
crashing — check `GET /threads/{thread_id}/state` for the graph's own
`status` field, which is `"failed"` when lesson validation exhausted its
retries.

## Debugging

When an agent session is stuck in a loop on the same failure: stop, strip the
change back to the smallest version that still reproduces the problem, and
write down what was tried and what happened before trying a different
approach. Use a fenced block with four backticks when quoting output that
itself contains triple-backtick fences.

## Pull requests

One subject per pull request. Unrelated cleanup found along the way belongs
in its own commit, and usually in its own pull request.

Discuss a substantial change via an issue before making it.

Before opening a pull request, remove branch-internal narrative from the
commits (see
[the published-release test](WRITING.md#slop-prevention)): fold a fixup into
its causal commit with `git rebase --autosquash`, or squash the branch into
one commit at its tip.

Commit format is in [WRITING.md](WRITING.md#commits).

## Decorum

- Participants will be tolerant of opposing views.
- Participants must ensure that their language and actions are free of
  personal attacks and disparaging personal remarks.
- When interpreting the words and actions of others, participants should
  always assume good intentions.
- Behavior which can be reasonably considered harassment will not be
  tolerated.

Based on [Ruby's Community Conduct Guideline](https://www.ruby-lang.org/en/conduct/).

## Security

This repository has no `SECURITY.md`. Report a vulnerability privately
through GitHub's Security tab ("Report a vulnerability") rather than a public
issue.
