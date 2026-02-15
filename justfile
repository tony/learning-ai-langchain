# Start LangGraph Studio dev server with Cloudflare tunnel
studio:
    uv run langgraph dev --tunnel --no-browser

# Run tests
test:
    uv run pytest

# Run linter
lint:
    uv run ruff check .

# Run linter with auto-fix
lint-fix:
    uv run ruff check . --fix --show-fixes

# Run type checker
typecheck:
    uv run mypy lesson_generator react_agent

# Format code
fmt:
    uv run ruff format .
