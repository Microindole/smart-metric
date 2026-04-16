from __future__ import annotations

from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths


class ServeCommand(BaseCommand):
    path = ("serve",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=5000)
        parser.add_argument("--debug", action="store_true")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        ensure_runtime_paths()
        from app import app

        app.run(host=args.host, port=args.port, debug=args.debug)
        return 0
