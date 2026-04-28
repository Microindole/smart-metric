from __future__ import annotations

from typing import Iterable


def analyze_oo_files(files: Iterable[dict], language: str | None = None) -> dict:
    from .service import analyze_oo_files as _analyze_oo_files

    return _analyze_oo_files(files, language)


__all__ = ["analyze_oo_files"]
