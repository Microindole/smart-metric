from __future__ import annotations

from flask import Blueprint, jsonify, request

from core.cfg_metric import analyze_cfg_files, analyze_imported_graph
from core.function_point_metric.service import calculate_function_point_metrics, default_function_point_payload


metrics_45_bp = Blueprint("metrics_45", __name__)


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@metrics_45_bp.get("/api/metrics/function-point/defaults")
def function_point_defaults():
    return ok(default_function_point_payload())


@metrics_45_bp.post("/api/metrics/function-point/calculate")
def function_point_calculate():
    try:
        payload = request.get_json(silent=True) or {}
        result = calculate_function_point_metrics(payload)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@metrics_45_bp.post("/api/metrics/cfg/calculate")
def cfg_calculate():
    try:
        upload_files = request.files.getlist("files")
        if not upload_files:
            return fail("请至少上传一个源码文件")

        language = request.form.get("language") or None
        files = [{"filename": f.filename, "content": f.read()} for f in upload_files]
        result = analyze_cfg_files(files, language)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@metrics_45_bp.post("/api/metrics/cfg/import-graph")
def cfg_import_graph():
    try:
        graph_file = request.files.get("file")
        if not graph_file:
            return fail("请上传控制流图文件")

        result = analyze_imported_graph(graph_file.read(), graph_file.filename)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)
