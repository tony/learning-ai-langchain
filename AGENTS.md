# AGENTS.md

learning-ai-langchain is a personal study project for LangChain and
LangGraph: a minimal ReAct tool-calling agent (`react_agent`), and a
LangGraph pipeline that generates and self-validates Python lesson files for
other study repositories (`lesson_generator`).

Follow the conventions already in the tree, and keep a change scoped to what
was asked for.

## What is here

| Path                        | What it is                                                              |
| ---------------------------- | ------------------------------------------------------------------------ |
| `react_agent/`               | ReAct agent (`create_agent`, `create_react_graph`) with one tool         |
| `lesson_generator/`           | Graph that generates, validates, and writes a lesson for a domain        |
| `lesson_generator/domains.py` | Registry of domains (`dsa`, `asyncio`) and their target project paths    |
| `lesson_generator/tools.py`   | File I/O and `validate_in_temp`, the ruff/mypy/pytest validation pipeline |
| `lesson_generator/templates/` | Built-in `.tmpl` fallback lesson template per pedagogy style             |
| `tests/`                      | pytest suite for both packages                                          |
| `langgraph.json`              | LangGraph dev server config; registers both graphs                      |
| `justfile`                    | Gate commands: `fmt`, `lint`, `lint-fix`, `typecheck`, `test`, `studio`  |

## Which policy applies

- Documentation, user-facing text, commit messages, docstrings, and source
  comments: [.github/WRITING.md](.github/WRITING.md)
- Environment, the gates, tests, and the LangGraph dev server:
  [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)

Each of those is the single home for its subject. Where a rule seems to be
stated twice, the file listed above is the one that governs.

## Change discipline

- Make the smallest coherent change that solves the verified problem; keep
  unrelated cleanup out of it.
- Reuse an existing file, helper, API, or test before adding a new one.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized module — not for a
  single-use helper or a one-line re-export.
- Keep new APIs private until a caller outside the module needs them.
- Add a test for every user-visible behavior change.
- A passing gate is evidence only once it has been shown capable of failing.
  Pair a new test with a deliberate break that proves it bites.

Both domains in `lesson_generator/domains.py` point at sibling study
repositories under `~/study/python/` (override with `LESSON_STUDY_ROOT`) that
are not part of this repository; neither needs to exist, since generation
falls back to a built-in template and a temp output directory when it does
not. `langchain-openai` is a declared dependency but nothing in this
repository constructs a `ChatOpenAI`; only `ChatAnthropic` is wired in today.

## References

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
