from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..help import render_all_help, render_help
from ..pager import show_with_pager


class HelpCommand(BaseCommand):
    path = ("help",)
    aliases = (("h",),)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("-a", "--all", action="store_true")
        parser.add_argument("topic", nargs="*")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        from ..registry import build_command_registry

        commands = build_command_registry().values()
        if args.all:
            text = render_all_help(commands, ctx)
        elif args.topic:
            text = render_help([*args.topic, "--help"], commands, ctx)
        else:
            text = render_help(["--help"], commands, ctx)
        show_with_pager(text)
        return 0
