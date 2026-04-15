from __future__ import annotations

from typing import Dict, Iterable, Tuple


def _validate_non_negative_int_map(counts: Dict[str, int], required_keys: Iterable[str], label: str) -> None:
    for key in required_keys:
        value = counts.get(key, 0)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{label}.{key} 必须是非负整数")


def weighted_sum(counts: Dict[str, int], weights: Dict[str, int], label: str) -> int:
    _validate_non_negative_int_map(counts, weights.keys(), label)
    return sum(int(counts.get(k, 0)) * int(w) for k, w in weights.items())


def factor_value(factors: Iterable[Dict], factor_type: str) -> Tuple[float, float]:
    total = 0.0
    for item in factors:
        weight = float(item.get("weight", 0))
        level = float(item.get("level", 0))
        total += weight * level

    if factor_type == "TCF":
        return total, 0.6 + 0.01 * total
    if factor_type == "EF":
        return total, 1.4 - 0.03 * total
    raise ValueError("factor_type 仅支持 TCF 或 EF")


def ucp_value(uuc: int, uaw: int, tcf: float, ef: float) -> float:
    return (uuc + uaw) * tcf * ef
