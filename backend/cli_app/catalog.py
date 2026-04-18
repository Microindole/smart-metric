from __future__ import annotations

import json
from pathlib import Path


SUPPORTED_LANGS = {"zh", "en"}
DEFAULT_LANG = "zh"
I18N_DIR = Path(__file__).resolve().parent / "i18n"


def resolve_lang(argv: list[str]) -> str:
    for index, token in enumerate(argv):
        if token == "--lang" and index + 1 < len(argv):
            candidate = argv[index + 1].lower()
            if candidate in SUPPORTED_LANGS:
                return candidate
        if token == "-L" and index + 1 < len(argv):
            candidate = argv[index + 1].lower()
            if candidate in SUPPORTED_LANGS:
                return candidate
        if token.startswith("--lang="):
            candidate = token.split("=", 1)[1].lower()
            if candidate in SUPPORTED_LANGS:
                return candidate
    return DEFAULT_LANG


def load_catalog(lang: str) -> dict:
    target = I18N_DIR / f"{lang}.json"
    if not target.exists():
        target = I18N_DIR / f"{DEFAULT_LANG}.json"
    return json.loads(target.read_text(encoding="utf-8"))
