from __future__ import annotations

import json
from argparse import Namespace, _SubParsersAction
from pathlib import Path

from ..base import BaseCommand, CliContext
from ..runtime import ensure_runtime_paths


ensure_runtime_paths()
from core.ai_review import build_ai_review_report_payload, run_ai_review  # noqa: E402
from core.project_metric import ProjectScanOptions  # noqa: E402
from core.report_export import export_report  # noqa: E402


class AIReviewCommand(BaseCommand):
    path = ("ai-review",)
    aliases = (("air",), ("review",))

    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        parser = subparsers.add_parser(self.path[0], add_help=False)
        parser.add_argument("path")
        parser.add_argument("-m", "--modules", default="inventory,loc,dependency,oo,design")
        parser.add_argument("-d", "--ignore-dir", action="append", default=[])
        parser.add_argument("-g", "--ignore-glob", action="append", default=[])
        parser.add_argument("-f", "--ignore-file", default=".smartmetricignore")
        parser.add_argument("-G", "--no-ignore-file", action="store_true")
        parser.add_argument("-D", "--no-default-ignore", action="store_true")
        parser.add_argument("-M", "--model", default="gpt-4.1-mini")
        parser.add_argument("-F", "--format", choices=("json", "markdown", "html", "pdf"), default="json")
        parser.add_argument("-o", "--output", default="")
        parser.add_argument("-P", "--fp-file", default="")
        parser.add_argument("-E", "--estimate-file", default="")
        parser.add_argument("--phase1-file", default="")
        parser.add_argument("--phase2-file", default="")
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
        result = run_ai_review(
            str(root),
            modules,
            options,
            model=str(args.model or "gpt-4.1-mini"),
            function_point_payload=load_optional_json(args.fp_file),
            estimate_payload=load_optional_json(args.estimate_file),
            phase1_fixture=str(args.phase1_file or "").strip(),
            phase2_fixture=str(args.phase2_file or "").strip(),
        )
        if args.format == "json":
            output = Path(args.output) if args.output else root / "smartmetric-ai-review.json"
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(output)
            return 0

        report_payload = build_ai_review_report_payload(result)
        content = export_report(report_payload, args.format)
        output = Path(args.output) if args.output else root / default_suffix(args.format)
        output.write_bytes(content)
        print(output)
        return 0


def load_optional_json(path: str) -> dict | None:
    target = str(path or "").strip()
    if not target:
        return None
    return json.loads(Path(target).read_text(encoding="utf-8"))


def default_suffix(fmt: str) -> str:
    return {
        "markdown": "smartmetric-ai-review.md",
        "html": "smartmetric-ai-review.html",
        "pdf": "smartmetric-ai-review.pdf",
        "json": "smartmetric-ai-review.json",
    }[fmt]
