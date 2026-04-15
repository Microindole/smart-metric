from __future__ import annotations

from typing import Iterable, Optional

from .language_rules import detect_language
from .scanner import scan_lines


def _decode_bytes(content: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("文件编码无法识别")


def analyze_single_file(filename: str, content: bytes, language: Optional[str] = None) -> dict:
    detected = detect_language(filename, language)
    text = _decode_bytes(content)
    stats = scan_lines(text, detected)
    ratio = 0.0 if stats["total_lines"] == 0 else stats["comment_lines"] / stats["total_lines"]
    return {
        "filename": filename,
        "language": detected,
        **stats,
        "comment_ratio": round(ratio, 4),
    }


def analyze_files(files: Iterable[dict], language: Optional[str] = None) -> dict:
    results = []
    total = {"total_lines": 0, "blank_lines": 0, "comment_lines": 0, "code_lines": 0}

    for item in files:
        res = analyze_single_file(item["filename"], item["content"], language)
        results.append(res)
        for key in total:
            total[key] += res[key]

    total_ratio = 0.0 if total["total_lines"] == 0 else total["comment_lines"] / total["total_lines"]
    return {
        "files": results,
        "summary": {**total, "comment_ratio": round(total_ratio, 4)},
    }
