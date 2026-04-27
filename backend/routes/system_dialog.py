from __future__ import annotations

from flask import Blueprint, jsonify, request

from core.system_dialog import select_directory


system_dialog_bp = Blueprint("system_dialog", __name__, url_prefix="/api/system")


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@system_dialog_bp.post("/pick-directory")
def pick_directory():
    try:
        payload = request.get_json(silent=True) or {}
        initial_directory = str(payload.get("initial_directory") or "").strip() or None
        title = str(payload.get("title") or "").strip() or "选择项目目录"
        selected = select_directory(initial_directory=initial_directory, title=title)
        if not selected:
            return fail("未选择目录", 409)
        return ok({"path": selected})
    except Exception as exc:
        return fail(str(exc), 422)
