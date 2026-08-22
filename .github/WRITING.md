# Writing

How this project writes prose, for humans and agents alike. It governs
`README.md`, commit messages, CLI output, docstrings, and source comments —
every surface a reader reaches. There is no `CHANGES` file, no release notes,
and nothing published to PyPI, so those conventions do not apply here.

For environment setup, the gates, and running the LangGraph dev server, see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Voice

Three surfaces, one voice. A docstring says what a caller may rely on; prose
says what happens; a commit message says why. All are present tense, lead
with the thing being described, and stop. Why it was built that way belongs
in the commit message, which is timestamped and attached to the diff.

The most useful editing operation is deleting the introductory sentence.

Lead with verbs and name concrete things. Put identifiers in backticks. Prefer
short declarative sentences, one operational fact each. Do not explain Python
to Python developers; do explain this project's semantics.

Type annotations describe shape. Documentation describes meaning. A sentence
that restates a signature has said nothing.

Use MUST, SHOULD, and MAY only where the normative sense is meant. Say what
actually happens rather than that something is "supported".

| Instead of                       | Prefer                             |
| --------------------------------- | ----------------------------------- |
| "We added…"                      | "`create_agent` now accepts…"       |
| "New and improved"               | "`list_domains` now…"               |
| "powerful", "seamless"           | state the capability                |
| "easily", "simply", "just"       | omit                                 |
| "simple", "obvious", "intuitive" | omit                                 |
| "robust"                         | name the failure that is handled    |
| "comprehensive"                  | name what is covered                |
| "production-ready"               | state the guarantee                 |
| "optimized", "blazingly fast"    | give the magnitude                  |
| "various fixes"                  | name the components                 |
| "under the hood"                 | omit unless observable              |
| "please note that", "note that"  | state the fact                      |
| "leverage", "utilize"            | "use"                                |
| "delve into"                     | "read", or omit                     |
| "best practices"                 | name the practice                   |
| "in order to"                    | "to"                                 |

## Who you are writing for

The default reader is the project's owner, coming back to it after a break, or
someone extending `lesson_generator` with a new domain. They know Python and
LangGraph; they do not remember which module owns which state field. Serve
that reader: say what a function does before its signature, and keep advanced
material — the retry/fix loop, the validation subprocess pipeline — clearly
marked so a reader who only wants to run the agent can stop after the first
section.

## README

A README is the shortest path from "what is this?" to competent use, not the
project's autobiography.

State the minimum Python version in prose — `requires-python` in
`pyproject.toml` is the authority; the README must agree with it. Name the two
runnable entry points (`react_agent`, `lesson_generator`) as `python -m`
invocations; neither ships a console script, so `python -m <package>` is the
only way to run either.

Document the semantic model, not the flag list. `--help` already enumerates
`lesson_generator`'s flags; what it cannot say is what goes to stdout versus
stderr, and what a non-zero exit means. State defaults explicitly — defaults
are API. State negative guarantees where they exist: `lesson_generator`
refuses to overwrite an existing lesson file without `--force`, and refuses to
write outside the resolved output directory.

Headings stay conventional and stable, because people deep-link them.

## API keys

`.env.example` lists `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and
`LANGSMITH_API_KEY`; both entry points call `load_dotenv()` before touching a
model. A real key never appears in prose, an example, a docstring, or a
committed config file — only the placeholder names above, and only in
`.env.example`. `.env` itself is gitignored.

## Documented examples that run

Nothing in this repository collects a `>>> ` prompt today. `pytest`'s
`addopts` in `pyproject.toml` set `--tb=short`, `--no-header`, `--showlocals`,
`--strict-markers`, and `--durations=5` — there is no `--doctest-modules`, no
`--doctest-glob`, no `testpaths`, and `tests/conftest.py` defines no
`doctest_namespace` fixture. A `>>> ` block in a docstring or in this README
is prose that looks like a test; nothing runs it, and it can be wrong for
years.

Given that, do not add a `>>> `-prompted block anywhere in this repository
expecting the suite to execute it — it will not, and a green `pytest` run
will not tell you it broke. Show example output as a plain fenced block or, if
the behavior is worth pinning down, as a real `test_*` function in `tests/`.

Doctests do run elsewhere in this project's lifecycle, just not as part of
`pytest` collecting this repo's own sources: `validate_in_temp` in
`lesson_generator/tools.py` writes generated code to a temp file and shells
out to `pytest --doctest-modules` against it as one of its validation steps,
adding `-o doctest_optionflags=ELLIPSIS NORMALIZE_WHITESPACE` when a domain's
`doctest_strategy` is `"ellipsis"`. That is the product's own quality gate on
LLM-generated lesson code, not a mechanism that executes examples written in
this repository's docs.

## Docstrings

The prime directive: never restate the type. The annotation is the source of
truth; the docstring carries what the annotation cannot.

Document instead the dimensions the type system cannot encode: what a call
mutates, what it raises and when, what "the next number" or "the resolved
directory" means, and any ordering or idempotence guarantee.

The first sentence stands alone; tooling truncates there. PEP 257 applies:
triple double quotes, an imperative one-line summary ending in a period, a
blank line before any extended description.

This repository uses the NumPy docstring convention (`ruff`'s
`pydocstyle.convention = "numpy"`), enforced by the linter rather than
relitigated in review:

```python
"""Short description of the function or class.

Parameters
----------
param1 : type
    Description of param1.

Returns
-------
type
    Description of the return value.
"""
```

## Source comments

A comment ships only if it passes all three gates. Fail any: delete or
rewrite. Borderline: delete — borderline means the information is
reconstructible, which is what makes deletion cheap.

**Loss.** Three years from now, would losing this cost a maintainer real time
rediscovering intent, an invariant, a constraint, or a failure mode the code
and tests do not already make obvious?

**Elite.** Would SQLite, Redis, the Go standard library, or CPython write this
comment, at this length? Those projects state the constraint and stop. They do
not argue with an imagined objector.

**Upkeep.** Will it stay true without maintenance? A comment that hand-syncs a
value the code owns — a count, an offset, a line reference, a duplicated
constant — is false the first time that value moves.

### Ceiling

One or two lines. A comment reaching four is either carrying several facts, in
which case split it, or arguing, in which case cut it to the fact.

Rationale, alternatives weighed, and the story of how the code got here belong
in the commit message: timestamped, attached to the exact diff, and free to
maintain.

### Keep

- Why over how: upstream quirks, protocol and compatibility constraints,
  performance tradeoffs still part of the contract.
- Invariants, preconditions, ordering, lifetime, and concurrency requirements
  that types and tests cannot express.
- Code that looks wrong but is not, so a later cleanup does not reintroduce
  the bug.
- A high-level sketch of an algorithm whose local operations do not reveal the
  whole.

### Delete

- Narration of the next lines; code translated into English.
- Restated names, types, defaults, or control flow.
- Values duplicated from the code and hand-synced.
- Justification, hedging, or apology for a choice.
- Speculation about future requirements.
- History version control already holds, including commented-out code.
- Ticket and issue numbers — this project does not track one, and a bare
  number says nothing to a reader without tracker access.
- Transient observations — "currently", "for now", "the latest release" —
  that go stale with no nearby edit.

### The upkeep gate in practice

It reaches values that track our own code. It does not reach frozen external
facts.

Bad (Delete):

```python
# There are 40 tests to complete for the graph module.
```

Good (Keep):

```python
# The dev server classifies factories by parameter count, so this
# wrapper takes no arguments even though create_agent takes one.
```

### Documentation exception

Minimal usage examples, and parameter, return, and raises entries on public
API, are exempt from the loss gate — they serve the caller, not the
maintainer. They are exempt from nothing else. Ceiling: a good man page entry.

## Terminology and capitalization

Pick the domain noun and keep it. A learning topic is a **domain** (`dsa`,
`asyncio`), never a "subject" or "track". A generated file is a **lesson**,
never a "chapter" or "module". The generation approach is a **pedagogy
style** (`concept_first`, `integration_first`, `application_first`); write
"pedagogy" consistently rather than alternating with "teaching mode" or
"style" alone.

## Markdown

Prose wraps at 80 columns. Table rows, badge lines, and long links are exempt,
because breaking them harms rendering.

GitHub alert blocks — `> [!NOTE]`, `> [!WARNING]` — render as literal text
outside GitHub, so reserve them for at most one load-bearing warning per
document.

Do not use a local absolute path or an email address in anything published.

## Code blocks

Code blocks are paste-and-run units: pasting one block runs exactly one
intended action.

- **One command per block.** Multiple steps may share a block only when
  explicitly chained with `&&`, `;`, or `\` continuations — the chain is then
  one logical command.
- **Explanations go in prose above the block**, never as `#` comments inside
  it.
- **Command menus are per-command blocks with prose lead-ins**, not tables.
- **Shell commands use the `console` tag with a `$ ` prefix.** This separates
  interactive commands from scripts and enables prompt-aware copy.
- **Split long commands with `\`** — one flag or flag+value pair per indented
  continuation line, positional arguments last.

Good — run the lesson generator against a domain:

```console
$ uv run python -m lesson_generator \
    --domain dsa \
    --topic "binary search"
```

Bad:

```console
# Run the lesson generator against a domain
$ uv run python -m lesson_generator --domain dsa --topic "binary search"
```

## Commits

```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.

what:
- Specific technical changes made
- Focused on a single topic
```

Keep the subject to 50 characters or fewer, excluding any trailing `(#NN)`
pull request reference, and wrap body lines at 72. Separate the `why:` and
`what:` blocks with a blank line.

Routine maintenance commits drop the colon and take a capitalized
description, which is what distinguishes them at a glance in
`git log --oneline`:

```
py(deps[dev]) Bump dev packages
ai(rules[AGENTS]) Judge comments by three gates
```

Everything that changes behavior keeps the colon.

Common types used in this repository:

- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev dependencies
- **ai(rules[AGENTS])**: `AGENTS.md` rule updates
- **ai(claude[rules])**: `CLAUDE.md` rule updates

For a multi-line message, use a heredoc so the formatting survives:

```console
$ git commit -m "$(cat <<'EOF'
Scope(feat[detail]): Concise description

why: Explanation of the change.

what:
- First change
- Second change
EOF
)"
```

## Slop prevention

Treat AI slop as review-hostile noise, not as proof that text or code is
wrong. The goal is to maximize information density.

- **AI signatures.** No "Generated by", no conversational filler, no
  unexplained emoji, no tool metadata.
- **Brittle references.** No hard-coded line numbers, fragile file or test
  counts, dated "as of" claims, bare SHAs, or local absolute paths — unless
  they are strict evidentiary artifacts such as a benchmark log or a
  lockfile entry, which are exempt.
- **Diff narration.** Do not restate what moved, was renamed, or was removed
  in anything the reader holds alongside the diff: code, docstrings, README,
  or a pull request description. The diff and the commit message already
  carry it.
- **Branch-internal narrative.** Do not mention intermediate states,
  abandoned approaches, or "no longer" behavior in a shipped artifact unless
  users of a published release actually experienced the old state — this
  project has never published a release, so treat every prior state as
  branch-internal by default (**the published-release test**).
- **Low-value scaffolding.** No ownerless TODOs, unused future-proofing,
  debug artifacts, or defensive wrappers around failure modes nothing can
  reach.
- **Prose inflation.** The diction table under [Voice](#voice) governs;
  replace an inflated word with a concrete description of behavior,
  constraints, or trade-offs.
- **Coded labels.** Write rules and findings as plain imperatives. No `[R1]`,
  `Option B`, or any index a reader has to decode. Internal agent bookkeeping
  may use ids; shipped text may not.

**Durable source links.** Link to a pinned revision, never to trunk. Prefer a
7-character commit SHA reachable from `main`; a `blob/main/…` link rots
silently as the file moves and the anchor lands on unrelated code while still
resolving. Reserve `blob/main/…` for a living document meant to always show
the latest state. A line anchor (`#L120-L145`) is only safe on a pinned ref.

Preserve the "why". Never delete a comment documenting an invariant, a
protocol constraint, a platform quirk, or an upstream workaround — those are
the facts [Source comments](#source-comments) keeps, and every other comment
is judged by it.
