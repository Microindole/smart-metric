from __future__ import annotations

from flask import Blueprint, jsonify, request
from pathlib import Path
import json

from core.ai_review import build_ai_review_report_payload, run_ai_review
from core.ai_review.config import summarize_ai_review_config


ai_review_bp = Blueprint("ai_review", __name__, url_prefix="/api/metrics/ai-review")


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@ai_review_bp.post("/run")
def run_review():
    try:
        payload = request.get_json(silent=True) or {}
        project_path = str(payload.get("path") or "").strip()
        if not project_path:
            return fail("请提供项目目录路径")

        modules = payload.get("modules") or None
        options = {
            "use_default_ignores": payload.get("use_default_ignores", True),
            "ignore_dirs": payload.get("ignore_dirs") or [],
            "ignore_globs": payload.get("ignore_globs") or [],
            "use_ignore_file": payload.get("use_ignore_file", True),
            "ignore_file_name": payload.get("ignore_file_name") or ".smartmetricignore",
        }
        result = run_ai_review(
            project_path,
            modules,
            options,
            model=str(payload.get("model") or "gpt-4.1-mini"),
            function_point_payload=resolve_optional_json(payload.get("function_point_payload"), payload.get("fp_file")),
            estimate_payload=resolve_optional_json(payload.get("estimate_payload"), payload.get("estimate_file")),
            phase1_fixture=str(payload.get("phase1_file") or "").strip(),
            phase2_fixture=str(payload.get("phase2_file") or "").strip(),
            phase1_payload=payload.get("phase1_payload") or None,
            phase2_payload=payload.get("phase2_payload") or None,
        )
        return ok({"review": result, "report": build_ai_review_report_payload(result)})
    except Exception as exc:
        return fail(str(exc), 422)


@ai_review_bp.get("/config")
def ai_review_config():
    try:
        return ok(summarize_ai_review_config())
    except Exception as exc:
        return fail(str(exc), 422)


def resolve_optional_json(inline_payload, path_value) -> dict | None:
    if isinstance(inline_payload, dict) and inline_payload:
        return inline_payload
    target = str(path_value or "").strip()
    if not target:
        return None
    return json.loads(Path(target).read_text(encoding="utf-8"))
