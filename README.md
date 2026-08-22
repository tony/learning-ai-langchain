# learning-ai-langchain

A personal study project for [LangChain](https://github.com/langchain-ai/langchain)
and [LangGraph](https://github.com/langchain-ai/langgraph): a minimal ReAct
tool-calling agent (`react_agent`), and a LangGraph pipeline that generates
and self-validates Python lesson files for other study repositories
(`lesson_generator`).

Requires Python 3.13 or newer.

## Setup

```console
$ uv sync
```

`[tool.uv.sources]` in `pyproject.toml` points the LangChain and LangGraph
dependencies at local editable checkouts under `../../../study/ai-agents/`
relative to this repository; `uv sync` fails without those sibling
checkouts present.

```console
$ cp .env.example .env
```

Fill in `ANTHROPIC_API_KEY` — both graphs default to `ChatAnthropic`. The
dev dependencies include `langchain-openai`, but neither graph constructs a
`ChatOpenAI` today; `OPENAI_API_KEY` and `LANGSMITH_API_KEY` in `.env.example`
are unused placeholders. A real key belongs only in `.env`, which is
gitignored — never in a command, an issue, or a commit.

## Running the ReAct agent

```console
$ uv run python -m react_agent
```

Runs the default query ("What is the weather in SF?") against the `search`
tool. Pass a custom query as arguments:

```console
$ uv run python -m react_agent "What is the weather in SF?"
```

Each message in the resulting conversation is printed to stdout as
`<type>: <content>`.

## Generating a lesson

```console
$ uv run python -m lesson_generator --list-domains
```

Two domains are registered: `dsa` and `asyncio`. Each points at a sibling
study project under `~/study/python/` (override the root with
`LESSON_STUDY_ROOT`), used to read that project's lesson template and count
its existing lessons. Neither needs to exist on disk: without it,
`lesson_generator` falls back to a built-in template and starts numbering
from 1, and without `--out` it writes to a temp directory keyed by user and
domain rather than the study project.

```console
$ uv run python -m lesson_generator \
    --domain dsa \
    --topic "binary search"
```

The graph asks the model to draft a lesson, then validates the result —
`ruff format`, `ruff check`, `mypy`, and `pytest --doctest-modules` — retrying
up to `--max-retries` times (default 3, maximum 10). On success the lesson is
written under the domain's lesson directory, numbered one past the highest
existing lesson; it refuses to overwrite an existing file unless `--force` is
given, and never writes outside the resolved output directory. `--dry-run`
runs validation only and prints the rendered code to stdout instead of
writing it. On failure the process exits non-zero and prints the validation
errors to stderr.

## LangGraph Studio

Both graphs are also registered with the LangGraph dev server in
`langgraph.json`. See
[CONTRIBUTING.md](.github/CONTRIBUTING.md#running-the-langgraph-dev-server)
for how to start it and query its HTTP API.

## Development

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the gates and the test
suite, and [WRITING.md](.github/WRITING.md) for how this project writes
prose.
