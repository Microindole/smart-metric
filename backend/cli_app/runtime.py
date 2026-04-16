from __future__ import annotations

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT = BACKEND_DIR.parent
SCRIPTS_DIR = ROOT / "scripts"


def ensure_runtime_paths() -> None:
    for target in (ROOT, BACKEND_DIR, SCRIPTS_DIR):
        value = str(target)
        if value not in sys.path:
            sys.path.insert(0, value)
