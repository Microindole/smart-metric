from __future__ import annotations

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from core.diagram_parser import parse_usecase_diagram
from core.export_service import export_rows_to_csv
from core.loc_metric import analyze_files
from core.samples import list_samples, read_sample
from core.usecase_metric.defaults import EF_DEFAULT_FACTORS, TCF_DEFAULT_FACTORS
from core.usecase_metric.service import calculate_usecase_metrics, parse_oom_and_suggest_counts
from routes.metrics_45 import metrics_45_bp
from routes.metrics_oo_estimate import metrics_oo_estimate_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(metrics_45_bp)
app.register_blueprint(metrics_oo_estimate_bp)


def ok(data=None):
    return jsonify({"success": True, "data": data})


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


@app.get("/api/health")
def health():
    return ok({"status": "ok"})


@app.get("/api/metrics/usecase/default-factors")
def default_factors():
    return ok({"tcf_factors": TCF_DEFAULT_FACTORS, "ef_factors": EF_DEFAULT_FACTORS})


@app.post("/api/metrics/usecase/parse-oom")
def parse_oom():
    try:
        f = request.files.get("file")
        if not f:
            return fail("请上传 .oom 文件")
        parsed = parse_usecase_diagram(f.filename, f.read())
        suggested = parse_oom_and_suggest_counts(parsed)
        return ok(suggested)
    except Exception as exc:
        return fail(str(exc), 422)


@app.post("/api/metrics/usecase/calculate")
def usecase_calculate():
    try:
        payload = request.get_json(silent=True) or {}
        result = calculate_usecase_metrics(payload)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@app.post("/api/metrics/loc/calculate")
def loc_calculate():
    try:
        upload_files = request.files.getlist("files")
        if not upload_files:
            return fail("请至少上传一个源码文件")

        language = request.form.get("language") or None
        files = [{"filename": f.filename, "content": f.read()} for f in upload_files]
        result = analyze_files(files, language)
        return ok(result)
    except Exception as exc:
        return fail(str(exc), 422)


@app.post("/api/export")
def export_csv():
    try:
        payload = request.get_json(silent=True) or {}
        rows = payload.get("rows", [])
        filename = payload.get("filename", "metric-export.csv")

        csv_bytes = export_rows_to_csv(rows)
        if not csv_bytes:
            return fail("无可导出的数据")

        from io import BytesIO

        return send_file(
            BytesIO(csv_bytes),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        return fail(str(exc), 422)


@app.get("/api/samples")
def samples():
    return ok({"items": list_samples()})


@app.get("/api/samples/<sample_name>")
def get_sample(sample_name: str):
    try:
        content, name = read_sample(sample_name)
        from io import BytesIO

        return send_file(BytesIO(content), as_attachment=True, download_name=name)
    except Exception as exc:
        return fail(str(exc), 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
