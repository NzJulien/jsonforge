"""Command-line interface for jsonforge.

Usage:
    jsonforge infer file1.json [file2.json ...] [-o schema.json] [-t "Title"]
    jsonforge validate data.json schema.json
    jsonforge diff old.json new.json
"""
from __future__ import annotations

import argparse
import sys

from .differ import diff
from .inferencer import infer_schema
from .utils import Color, colorize, load_json, print_json, save_json
from .validator import validate


def cmd_infer(args: argparse.Namespace) -> int:
    samples = [load_json(p) for p in args.files]
    schema = infer_schema(samples if len(samples) > 1 else samples[0], title=args.title)
    if args.output:
        save_json(schema, args.output)
        print(colorize(f"Schema written to {args.output}", Color.GREEN))
    else:
        print_json(schema)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    instance = load_json(args.data)
    schema = load_json(args.schema)
    result = validate(instance, schema)
    if result.is_valid:
        print(colorize(f"VALID: {args.data} satisfies {args.schema}", Color.GREEN))
        return 0
    print(colorize(f"INVALID: {len(result.errors)} error(s) found", Color.RED))
    for err in result.errors:
        print("  " + colorize(str(err), Color.YELLOW))
    return 1


def cmd_diff(args: argparse.Namespace) -> int:
    old = load_json(args.old)
    new = load_json(args.new)
    changes = diff(old, new)
    if not changes:
        print(colorize("No differences found.", Color.GREEN))
        return 0
    colors = {"added": Color.GREEN, "removed": Color.RED, "changed": Color.YELLOW}
    for change in changes:
        print(colorize(str(change), colors[change.kind]))
    print(colorize(f"\n{len(changes)} change(s) found.", Color.BOLD))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jsonforge", description="Infer, validate, and diff JSON data.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_infer = sub.add_parser("infer", help="Infer a JSON Schema from sample document(s)")
    p_infer.add_argument("files", nargs="+", help="One or more sample JSON files")
    p_infer.add_argument("-o", "--output", help="Write schema to this file instead of stdout")
    p_infer.add_argument("-t", "--title", default="Inferred Schema", help="Schema title")
    p_infer.set_defaults(func=cmd_infer)

    p_validate = sub.add_parser("validate", help="Validate a JSON document against a schema")
    p_validate.add_argument("data", help="JSON document to validate")
    p_validate.add_argument("schema", help="JSON Schema file")
    p_validate.set_defaults(func=cmd_validate)

    p_diff = sub.add_parser("diff", help="Show structural differences between two JSON documents")
    p_diff.add_argument("old", help="Original JSON file")
    p_diff.add_argument("new", help="Updated JSON file")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
