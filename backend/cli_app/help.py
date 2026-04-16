from __future__ import annotations

from typing import Iterable

from .base import BaseCommand, CliContext


def render_help(argv: list[str], commands: Iterable[BaseCommand], ctx: CliContext) -> str:
    command_map = {command.key: command for command in commands}
    target_key = resolve_command_key(argv, command_map)
    if target_key and target_key in command_map:
        return render_command_help(target_key, ctx)
    return render_root_help(ctx)


def resolve_command_key(argv: list[str], command_map: dict[str, BaseCommand]) -> str:
    tokens: list[str] = []
    skip_next = False
    for index, token in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if token in ("-h", "--help"):
            break
        if token == "--lang":
            skip_next = True
            continue
        if token.startswith("--lang=") or token.startswith("-"):
            continue
        tokens.append(token)
    for length in range(len(tokens), 0, -1):
        key = ".".join(tokens[:length])
        if key in command_map:
            return key
    return ""


def render_root_help(ctx: CliContext) -> str:
    global_text = ctx.catalog["global"]
    lines = [
        f"{global_text['prog']} - {global_text['description']}",
        "",
        f"{global_text['usage_label']}:",
        f"  {global_text['usage']}",
        "",
        f"{global_text['commands_label']}:",
    ]
    for name, summary in ctx.catalog["root_commands"].items():
        lines.append(f"  {name:<12} {summary}")
    lines.extend(
        [
            "",
            f"{global_text['options_label']}:",
            f"  --lang <zh|en>  {global_text['lang_option']}",
            f"  -h, --help      {global_text['help_option']}",
        ]
    )
    return "\n".join(lines)


def render_command_help(key: str, ctx: CliContext) -> str:
    global_text = ctx.catalog["global"]
    command = ctx.catalog["commands"][key]
    lines = [
        f"{global_text['prog']} {command['path']} - {command['summary']}",
        "",
        f"{global_text['usage_label']}:",
        f"  {command['usage']}",
    ]

    arguments = command.get("arguments", {})
    if arguments:
        lines.extend(["", f"{global_text['arguments_label']}:"])
        for name, description in arguments.items():
            lines.append(f"  {name:<18} {description}")

    options = command.get("options", {})
    if options:
        lines.extend(["", f"{global_text['options_label']}:"])
        for name, description in options.items():
            lines.append(f"  {name:<18} {description}")

    return "\n".join(lines)
