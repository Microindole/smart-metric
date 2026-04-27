from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "backend" / "config"
LOCAL_CONFIG_PATH = CONFIG_DIR / "ai_review.local.json"
EXAMPLE_CONFIG_PATH = CONFIG_DIR / "ai_review.example.json"


DEFAULT_CONFIG = {
    "planner": {
        "provider": "openai_compat",
        "model": "gpt-4.1-mini",
        "apiKey": "",
        "apiBase": "",
    },
    "memory": {
        "enabled": True,
        "autoCompact": True,
        "compactOnComplete": True,
        "compactOnFailure": True,
        "retrievalScope": "global",
        "retrievalStrength": "standard",
        "cleanupEnabled": True,
        "cleanupIntervalHours": 24,
    },
    "push": {
        "enabled": True,
        "onSessionComplete": True,
        "onSessionFailure": False,
    },
}


def load_ai_review_config() -> dict:
    config = json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))
    if LOCAL_CONFIG_PATH.exists():
        loaded = json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))
        config = deep_merge(config, loaded)

    planner = config.setdefault("planner", {})
    planner["apiKey"] = os.getenv("OPENAI_API_KEY", planner.get("apiKey", ""))
    planner["apiBase"] = os.getenv("OPENAI_API_BASE", planner.get("apiBase", ""))
    planner["model"] = os.getenv("OPENAI_MODEL", planner.get("model", "gpt-4.1-mini"))
    return config


def summarize_ai_review_config() -> dict:
    config = load_ai_review_config()
    planner = config.get("planner", {})
    return {
        "local_config_path": str(LOCAL_CONFIG_PATH),
        "example_config_path": str(EXAMPLE_CONFIG_PATH),
        "local_config_exists": LOCAL_CONFIG_PATH.exists(),
        "provider": planner.get("provider", "openai_compat"),
        "model": planner.get("model", "gpt-4.1-mini"),
        "api_base": planner.get("apiBase", ""),
        "api_key_configured": bool(planner.get("apiKey", "")),
    }


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
