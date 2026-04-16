from __future__ import annotations

import argparse
import sys

from .base import CliContext
from .catalog import load_catalog, resolve_lang
from .help import render_help
from .registry import build_command_registry
from .runtime import ensure_runtime_paths


def main(argv: list[str] | None = None) -> int:
    ensure_runtime_paths()
    argv = list(sys.argv[1:] if argv is None else argv)
    lang = resolve_lang(argv)
    catalog = load_catalog(lang)
    ctx = CliContext(lang=lang, catalog=catalog)
    commands = build_command_registry()

    if "-h" in argv or "--help" in argv:
        print(render_help(argv, commands.values(), ctx))
        return 0

    parser = build_parser(ctx, commands)
    args = parser.parse_args(argv)
    command = commands[args.command_key]
    return command.run(args, ctx)


def build_parser(ctx: CliContext, commands: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, prog=ctx.catalog["global"]["prog"])
    parser.add_argument("--lang", choices=("zh", "en"), default=ctx.lang)
    parser.add_argument("-h", "--help", action="store_true")

    root_subparsers = parser.add_subparsers(dest="root_command")
    root_subparsers.required = True

    groups: dict[str, argparse._SubParsersAction] = {}
    for command in commands.values():
        if len(command.path) == 1:
            command.configure(root_subparsers, ctx)
            continue
        parent = command.path[0]
        if parent not in groups:
            parent_parser = root_subparsers.add_parser(parent, add_help=False)
            parent_parser.add_argument("-h", "--help", action="store_true")
            parent_parser.add_argument("--lang", choices=("zh", "en"), default=ctx.lang)
            groups[parent] = parent_parser.add_subparsers(dest=f"{parent}_command")
            groups[parent].required = True
        command.configure(groups[parent], ctx)
    return parser
