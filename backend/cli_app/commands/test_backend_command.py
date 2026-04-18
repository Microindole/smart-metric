from __future__ import annotations

import sys
from argparse import Namespace, _SubParsersAction

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths


class TestBackendCommand(BaseCommand):
    path = ("test", "backend")
    aliases = (("tb",), ("t", "b"), ("t", "backend"))

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[-1], add_help=False)
        parser.add_argument("-s", "--suite", choices=("unit", "smoke", "all"), default="all")
        parser.add_argument("-u", "--base-url", default="http://127.0.0.1:5000")
        parser.add_argument("-S", "--start-server", action="store_true")
        parser.add_argument("-H", "--host", default="127.0.0.1")
        parser.add_argument("-p", "--port", type=int, default=5000)
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        ensure_runtime_paths()
        from run_backend_tests import main as run_backend_tests_main

        argv = ["run_backend_tests.py", "--suite", args.suite, "--base-url", args.base_url]
        if args.start_server:
            argv.extend(["--start-server", "--host", args.host, "--port", str(args.port)])

        old_argv = sys.argv
        try:
            sys.argv = argv
            return run_backend_tests_main()
        finally:
            sys.argv = old_argv
