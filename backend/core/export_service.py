from __future__ import annotations

import csv
import io
from typing import Iterable


def export_rows_to_csv(rows: Iterable[dict]) -> bytes:
    rows = list(rows)
    if not rows:
        return b""

    headers = list(rows[0].keys())
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")
