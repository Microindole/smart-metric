from __future__ import annotations

import json
from argparse import Namespace, _SubParsersAction
from pathlib import Path

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths


ensure_runtime_paths()
from core.project_metric import ProjectScanOptions  # noqa: E402
from core.project_metric.reporting import build_project_report_payload  # noqa: E402
from core.report_export import export_report  # noqa: E402


class ProjectReportCommand(BaseCommand):
    path = ("project-report",)
    aliases = (("prj",), ("preport",))

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("path")
        parser.add_argument("-m", "--modules", default="inventory,loc,dependency,oo,design")
        parser.add_argument("-d", "--ignore-dir", action="append", default=[])
        parser.add_argument("-g", "--ignore-glob", action="append", default=[])
        parser.add_argument("-f", "--ignore-file", default=".smartmetricignore")
        parser.add_argument("-G", "--no-ignore-file", action="store_true")
        parser.add_argument("-D", "--no-default-ignore", action="store_true")
        parser.add_argument("-F", "--format", choices=("markdown", "html", "pdf"), default="pdf")
        parser.add_argument("-o", "--output", default="")
        parser.add_argument("-P", "--fp-file", default="")
        parser.add_argument("-E", "--estimate-file", default="")
        parser.add_argument("-t", "--title", default="")
        parser.add_argument("-S", "--subtitle", default="")
        parser.set_defaults(command_key=self.key)

    def run(self, args: Namespace, ctx: CliContext) -> int:
        root = Path(args.path).resolve()
        modules = [item.strip() for item in str(args.modules).split(",") if item.strip()]
        options = ProjectScanOptions(
            use_default_ignores=not bool(args.no_default_ignore),
            ignore_dirs=tuple(item.strip() for item in args.ignore_dir if str(item).strip()),
            ignore_globs=tuple(item.strip() for item in args.ignore_glob if str(item).strip()),
            use_ignore_file=not bool(args.no_ignore_file),
            ignore_file_name=str(args.ignore_file or ".smartmetricignore").strip() or ".smartmetricignore",
        )
        payload, _ = build_project_report_payload(
            str(root),
            modules,
            options,
            title=str(args.title or "").strip() or None,
            subtitle=str(args.subtitle or "").strip() or None,
            function_point_payload=load_optional_json(args.fp_file),
            estimate_payload=load_optional_json(args.estimate_file),
        )
        content = export_report(payload, args.format)
        output = Path(args.output) if args.output else root / default_report_name(root.name, args.format)
        output.write_bytes(content)
        print(output)
        return 0


def load_optional_json(path: str) -> dict | None:
    target = str(path or "").strip()
    if not target:
        return None
    return json.loads(Path(target).read_text(encoding="utf-8"))


def default_report_name(project_name: str, fmt: str) -> str:
    suffix = {"markdown": ".md", "html": ".html", "pdf": ".pdf"}[fmt]
    return f"{project_name}-smartmetric-report{suffix}"
