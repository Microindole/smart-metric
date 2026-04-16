from __future__ import annotations

import json
from argparse import Namespace, _SubParsersAction
from pathlib import Path

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths
from ..services import print_json


ensure_runtime_paths()
from core.function_point_metric.service import calculate_function_point_metrics  # noqa: E402


class FunctionPointCommand(BaseCommand):
    path = ("fp",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("file")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
        print_json(calculate_function_point_metrics(payload))
        return 0
