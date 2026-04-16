from __future__ import annotations

import json
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"


def wait_for_health(base_url: str, timeout_seconds: float = 20.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            payload = request_json("GET", f"{base_url}/api/health")
            if payload.get("success") and payload.get("data", {}).get("status") == "ok":
                return
        except Exception as exc:  # pragma: no cover - retry path
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"后端健康检查未通过: {last_error}")


def run_smoke_suite(base_url: str) -> list[str]:
    steps: list[str] = []

    health = request_json("GET", f"{base_url}/api/health")
    assert health["success"] is True
    assert health["data"]["status"] == "ok"
    steps.append("GET /api/health")

    fp_defaults = request_json("GET", f"{base_url}/api/metrics/function-point/defaults")
    assert fp_defaults["success"] is True
    assert len(fp_defaults["data"]["gsc_factors"]) == 14
    steps.append("GET /api/metrics/function-point/defaults")

    fp_payload = {
        "counts": {
            "EI": {"simple": 2, "average": 1, "complex": 0},
            "EO": {"simple": 1, "average": 0, "complex": 0},
            "EQ": {"simple": 1, "average": 0, "complex": 0},
            "ILF": {"simple": 1, "average": 0, "complex": 0},
            "EIF": {"simple": 0, "average": 1, "complex": 0},
        },
        "gsc": [3] * 14,
    }
    fp_result = request_json("POST", f"{base_url}/api/metrics/function-point/calculate", json_body=fp_payload)
    assert fp_result["success"] is True
    assert fp_result["data"]["ufp"] > 0
    steps.append("POST /api/metrics/function-point/calculate")

    estimate_payload = {
        "metric_type": "fp",
        "metric_value": 20,
        "productivity": 8,
        "team_size": 2,
    }
    estimate_result = request_json("POST", f"{base_url}/api/metrics/estimate/calculate", json_body=estimate_payload)
    assert estimate_result["success"] is True
    assert estimate_result["data"]["effort_hours"] == 160
    steps.append("POST /api/metrics/estimate/calculate")

    cfg_result = request_json(
        "POST",
        f"{base_url}/api/metrics/cfg/import-graph",
        files=[("file", SAMPLES / "cfg_demo.json")],
    )
    assert cfg_result["success"] is True
    assert cfg_result["data"]["cyclomatic_complexity"] >= 1
    steps.append("POST /api/metrics/cfg/import-graph")

    oo_diagram_result = request_json(
        "POST",
        f"{base_url}/api/metrics/oo/diagram-calculate",
        files=[("file", SAMPLES / "class_diagram_demo.xml")],
    )
    assert oo_diagram_result["success"] is True
    assert oo_diagram_result["data"]["summary"]["class_count"] >= 1
    steps.append("POST /api/metrics/oo/diagram-calculate")

    return steps


def request_json(
    method: str,
    url: str,
    *,
    json_body: dict | None = None,
    files: Iterable[tuple[str, Path]] | None = None,
) -> dict:
    headers: dict[str, str] = {}
    data: bytes | None = None

    if json_body is not None:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif files is not None:
        data, content_type = encode_multipart(files)
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - surfaced to caller
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} 返回 {exc.code}: {body}") from exc


def encode_multipart(files: Iterable[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = f"smartmetric-{int(time.time() * 1000)}"
    chunks: list[bytes] = []

    for field_name, path in files:
        filename = path.name
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")

    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"
