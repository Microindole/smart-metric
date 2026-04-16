from __future__ import annotations

from argparse import Namespace, _SubParsersAction
from pathlib import Path
import json

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths


ensure_runtime_paths()
from core.report_export import export_report  # noqa: E402


class ReportCommand(BaseCommand):
    path = ("report",)

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("file", help="报告 JSON 输入路径")
        parser.add_argument("--format", choices=("markdown", "html", "pdf"), default="markdown")
        parser.add_argument("--output", default="")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        source = Path(args.file)
        payload = json.loads(source.read_text(encoding="utf-8"))
        content = export_report(payload, args.format)
        output = Path(args.output) if args.output else source.with_suffix(default_suffix(args.format))
        output.write_bytes(content)
        print(output)
        return 0


def default_suffix(fmt: str) -> str:
    if fmt == "markdown":
        return ".md"
    if fmt == "html":
        return ".html"
    return ".pdf"
