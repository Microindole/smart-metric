from __future__ import annotations

from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "samples"


def list_samples() -> list[dict]:
    if not SAMPLE_DIR.exists():
        return []

    items = []
    for p in sorted(SAMPLE_DIR.glob("*")):
        if p.is_file():
            items.append({"name": p.name, "size": p.stat().st_size})
    return items


def read_sample(sample_name: str) -> tuple[bytes, str]:
    target = SAMPLE_DIR / sample_name
    if not target.exists() or not target.is_file():
        raise FileNotFoundError("样例文件不存在")
    return target.read_bytes(), target.name
