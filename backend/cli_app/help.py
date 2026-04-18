from __future__ import annotations

from typing import Iterable

from .base import BaseCommand, CliContext


def render_help(argv: list[str], commands: Iterable[BaseCommand], ctx: CliContext) -> str:
    commands = list(commands)
    command_map = {command.key: command for command in commands}
    target_key = resolve_command_key(argv, command_map)
    if target_key and target_key in command_map:
        return render_command_help(target_key, command_map[target_key], ctx)
    return render_root_help(commands, ctx)


def render_all_help(commands: Iterable[BaseCommand], ctx: CliContext) -> str:
    commands = list(commands)
    global_text = ctx.catalog["global"]
    lines = [render_root_help(commands, ctx)]

    detailed_keys = [command.key for command in commands if command.key != "help"]
    if detailed_keys:
        lines.extend(["", f"{global_text['all_commands_label']}:"])
        for key in detailed_keys:
            command_obj = next(command for command in commands if command.key == key)
            summary = ctx.catalog["commands"][key]["summary"]
            path = ctx.catalog["commands"][key]["path"]
            lines.append(f"  {path:<18} {summary}")
            aliases = infer_aliases(command_obj)
            if aliases:
                lines.append(f"  {'':<18} {global_text['aliases_label']}: {', '.join(aliases)}")
    return "\n".join(lines)


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


def render_root_help(commands: Iterable[BaseCommand], ctx: CliContext) -> str:
    global_text = ctx.catalog["global"]
    root_aliases = ctx.catalog.get("root_aliases", {})
    root_command_map = {command.path[0]: command for command in commands if len(command.path) == 1}
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
        aliases = root_aliases.get(name) or infer_aliases(root_command_map.get(name))
        if aliases:
            lines.append(f"  {'':<12} {', '.join(aliases)}")
    lines.extend(
        [
            "",
            f"{global_text['options_label']}:",
            f"  -L, --lang <zh|en> {global_text['lang_option']}",
            f"  -h, --help      {global_text['help_option']}",
        ]
    )
    return "\n".join(lines)


def render_command_help(key: str, command_obj: BaseCommand, ctx: CliContext) -> str:
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

    aliases = infer_aliases(command_obj)
    if aliases:
        lines.extend(["", f"{global_text['aliases_label']}:"])
        lines.append(f"  {', '.join(aliases)}")

    options = command.get("options", {})
    if options:
        lines.extend(["", f"{global_text['options_label']}:"])
        for name, description in options.items():
            lines.append(f"  {name:<18} {description}")

    return "\n".join(lines)


def infer_aliases(command: BaseCommand | None) -> list[str]:
    if not command:
        return []
    aliases: list[str] = []
    for alias in getattr(command, "aliases", ()):
        aliases.append(" ".join(alias))
    return aliases
