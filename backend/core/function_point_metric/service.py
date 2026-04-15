from __future__ import annotations

from copy import deepcopy
from typing import Dict, List


FUNCTION_TYPE_WEIGHTS = {
    "EI": {"simple": 3, "average": 4, "complex": 6},
    "EO": {"simple": 4, "average": 5, "complex": 7},
    "EQ": {"simple": 3, "average": 4, "complex": 6},
    "ILF": {"simple": 7, "average": 10, "complex": 15},
    "EIF": {"simple": 5, "average": 7, "complex": 10},
}

FUNCTION_TYPE_NAMES = {
    "EI": "外部输入",
    "EO": "外部输出",
    "EQ": "外部查询",
    "ILF": "内部逻辑文件",
    "EIF": "外部接口文件",
}

DEFAULT_GSC_FACTORS = [
    {"id": 1, "name": "数据通信", "level": 0},
    {"id": 2, "name": "分布式数据处理", "level": 0},
    {"id": 3, "name": "性能", "level": 0},
    {"id": 4, "name": "高频使用配置", "level": 0},
    {"id": 5, "name": "事务率", "level": 0},
    {"id": 6, "name": "在线数据输入", "level": 0},
    {"id": 7, "name": "最终用户效率", "level": 0},
    {"id": 8, "name": "在线更新", "level": 0},
    {"id": 9, "name": "复杂处理", "level": 0},
    {"id": 10, "name": "可重用性", "level": 0},
    {"id": 11, "name": "安装方便性", "level": 0},
    {"id": 12, "name": "操作方便性", "level": 0},
    {"id": 13, "name": "多地点", "level": 0},
    {"id": 14, "name": "易变更性", "level": 0},
]


def calculate_function_point_metrics(payload: Dict) -> Dict:
    counts = payload.get("counts") or {}
    factors: List[Dict] = payload.get("gsc_factors") or deepcopy(DEFAULT_GSC_FACTORS)

    details = []
    ufp = 0
    for func_type, weights in FUNCTION_TYPE_WEIGHTS.items():
        raw = counts.get(func_type, {})
        subtotal = 0
        levels = []
        for level, weight in weights.items():
            count = _non_negative_int(raw.get(level, 0))
            contribution = count * weight
            subtotal += contribution
            levels.append(
                {
                    "level": level,
                    "count": count,
                    "weight": weight,
                    "contribution": contribution,
                }
            )
        ufp += subtotal
        details.append(
            {
                "type": func_type,
                "name": FUNCTION_TYPE_NAMES[func_type],
                "subtotal": subtotal,
                "levels": levels,
            }
        )

    normalized_factors = []
    for index, default_factor in enumerate(DEFAULT_GSC_FACTORS):
        raw = factors[index] if index < len(factors) else default_factor
        level = _clamp_int(raw.get("level", 0), 0, 5)
        normalized_factors.append({**default_factor, "level": level})

    gsc_total = sum(item["level"] for item in normalized_factors)
    vaf = round(0.65 + 0.01 * gsc_total, 4)
    fp = round(ufp * vaf, 4)

    return {
        "counts": counts,
        "details": details,
        "gsc_factors": normalized_factors,
        "gsc_total": gsc_total,
        "ufp": ufp,
        "vaf": vaf,
        "fp": fp,
    }


def default_function_point_payload() -> Dict:
    return {
        "weights": FUNCTION_TYPE_WEIGHTS,
        "names": FUNCTION_TYPE_NAMES,
        "gsc_factors": deepcopy(DEFAULT_GSC_FACTORS),
    }


def _non_negative_int(value) -> int:
    return max(_clamp_int(value, 0, None), 0)


def _clamp_int(value, minimum: int, maximum: int | None) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum
    if number < minimum:
        return minimum
    if maximum is not None and number > maximum:
        return maximum
    return number
