from __future__ import annotations

from flask import Blueprint, jsonify, request

from core.project_metric import analyze_project_directory


project_metric_bp = Blueprint("project_metric", __name__, url_prefix="/api/metrics/project")


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@project_metric_bp.post("/scan")
def scan_project():
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
        return ok(analyze_project_directory(project_path, modules, options))
    except Exception as exc:
        return fail(str(exc), 422)
