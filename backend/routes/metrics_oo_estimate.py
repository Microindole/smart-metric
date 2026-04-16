from __future__ import annotations

from flask import Blueprint, jsonify, request

from core.class_diagram_metric import analyze_class_diagram_bytes
from core.estimate_metric import calculate_estimate
from core.oo_metric import analyze_oo_files


metrics_oo_estimate_bp = Blueprint("metrics_oo_estimate", __name__)


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@metrics_oo_estimate_bp.post("/api/metrics/oo/calculate")
def oo_calculate():
    try:
        upload_files = request.files.getlist("files")
        if not upload_files:
            return fail("请至少上传一个源码文件")

        language = request.form.get("language") or None
        files = [{"filename": f.filename, "content": f.read()} for f in upload_files]
        result = analyze_oo_files(files, language)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@metrics_oo_estimate_bp.post("/api/metrics/estimate/calculate")
def estimate_calculate():
    try:
        payload = request.get_json(silent=True) or {}
        result = calculate_estimate(payload)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@metrics_oo_estimate_bp.post("/api/metrics/oo/diagram-calculate")
def oo_diagram_calculate():
    try:
        upload_file = request.files.get("file")
        if not upload_file:
            return fail("请上传类图文件")
        result = analyze_class_diagram_bytes(upload_file.filename, upload_file.read())
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)
