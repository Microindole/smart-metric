from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
for target in (ROOT, BACKEND_DIR):
    value = str(target)
    if value not in sys.path:
        sys.path.insert(0, value)

from cli_app.__main__ import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
