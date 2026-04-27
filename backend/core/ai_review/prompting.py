from __future__ import annotations

from pathlib import Path

from .schemas import PHASE1_SCHEMA, PHASE2_SCHEMA


PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(name: str) -> str:
    target = PROMPT_DIR / name
    return target.read_text(encoding="utf-8")


def build_phase1_variables(context_text: str) -> dict:
    return {
        "context_text": context_text,
        "schema_text": schema_to_text(PHASE1_SCHEMA),
    }


def build_phase2_variables(review_context: str) -> dict:
    return {
        "review_context": review_context,
        "schema_text": schema_to_text(PHASE2_SCHEMA),
    }


def schema_to_text(schema: dict) -> str:
    import json

    return json.dumps(schema, ensure_ascii=False, indent=2)

