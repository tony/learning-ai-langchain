"""CLI entry point for lesson generation.

Usage::

    uv run python -m lesson_generator --domain dsa --topic "binary search"
    uv run python -m lesson_generator --list-domains
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from dotenv import load_dotenv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lesson_generator",
        description="Generate learning content for Python study projects.",
    )
    parser.add_argument(
        "--list-domains",
        action="store_true",
        help="Print available domains and exit.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        help="Domain name (e.g. dsa, asyncio).",
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Lesson topic to generate.",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="Explicit output file path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated code without writing to disk.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output file.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum validation retry attempts (default: 3).",
    )
    return parser


def main() -> None:
    """Run the lesson generator CLI."""
    load_dotenv()

    parser = _build_parser()
    args = parser.parse_args()

    # Lazy imports to avoid loading LangChain/LangGraph for --list-domains
    from lesson_generator.domains import (
        get_domain,
        list_domains,
        validate_environment,
    )

    if args.list_domains:
        for name in list_domains():
            domain = get_domain(name)
            print(f"  {name}: {domain.pedagogy.value} ({domain.project_type.value})")
        sys.exit(0)

    if not args.domain or not args.topic:
        parser.error("--domain and --topic are required.")

    config = get_domain(args.domain)

    # Determine output directory
    if args.out:
        target_dir = args.out.parent
    elif config.project_path:
        env_ok, env_msg = validate_environment(config)
        if not env_ok:
            print(f"Error: {env_msg}", file=sys.stderr)
            sys.exit(1)
        target_dir = config.project_path / config.lesson_dir
    else:
        parser.error(
            f"Domain {args.domain!r} has no project path. Use --out to specify "
            "an output location.",
        )

    from lesson_generator.graph import create_lesson_graph

    graph = create_lesson_graph()
    result = graph.invoke(
        {
            "topic": args.topic,
            "domain_name": args.domain,
            "target_dir": target_dir,
            "max_iterations": args.max_retries,
            "dry_run": args.dry_run,
            "force": args.force,
        },
    )

    status = result.get("status", "unknown")
    if status == "committed":
        print(f"Lesson written to: {result['output_path']}")
    elif status == "dry_run" and result.get("rendered_code"):
        print(result["rendered_code"])
    else:
        print(f"Generation failed (status={status}).", file=sys.stderr)
        errors = result.get("validation_errors", [])
        if errors:
            print("Validation errors:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
