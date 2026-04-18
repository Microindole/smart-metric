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
    commands = build_command_registry()
    argv = normalize_alias_argv(argv, commands)
    lang = resolve_lang(argv)
    catalog = load_catalog(lang)
    ctx = CliContext(lang=lang, catalog=catalog)

    if "-h" in argv or "--help" in argv:
        print(render_help(argv, commands.values(), ctx))
        return 0

    parser = build_parser(ctx, commands)
    args = parser.parse_args(argv)
    command = commands[args.command_key]
    return command.run(args, ctx)


def normalize_alias_argv(argv: list[str], commands: dict) -> list[str]:
    alias_map = build_alias_map(commands)
    if not alias_map:
        return argv

    prefix: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--lang" and index + 1 < len(argv):
            prefix.extend([token, argv[index + 1]])
            index += 2
            continue
        if token == "-L" and index + 1 < len(argv):
            prefix.extend([token, argv[index + 1]])
            index += 2
            continue
        if token.startswith("--lang=") or token in ("-h", "--help"):
            prefix.append(token)
            index += 1
            continue
        break

    rest = argv[index:]
    candidates: list[str] = []
    for token in rest:
        if token.startswith("-"):
            break
        candidates.append(token)
        if len(candidates) >= 2:
            break

    for length in range(min(2, len(candidates)), 0, -1):
        alias = tuple(candidates[:length])
        if alias in alias_map:
            canonical = list(alias_map[alias])
            return prefix + canonical + rest[length:]
    return argv


def build_alias_map(commands: dict) -> dict[tuple[str, ...], tuple[str, ...]]:
    alias_map: dict[tuple[str, ...], tuple[str, ...]] = {("t",): ("test",)}
    for command in commands.values():
        for alias in getattr(command, "aliases", ()):
            alias_map[tuple(alias)] = tuple(command.path)
    return alias_map


def build_parser(ctx: CliContext, commands: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, prog=ctx.catalog["global"]["prog"])
    parser.add_argument("-L", "--lang", choices=("zh", "en"), default=ctx.lang)
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
            parent_parser.add_argument("-L", "--lang", choices=("zh", "en"), default=ctx.lang)
            groups[parent] = parent_parser.add_subparsers(dest=f"{parent}_command")
            groups[parent].required = True
        command.configure(groups[parent], ctx)
    return parser
