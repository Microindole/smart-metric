from __future__ import annotations

from typing import Dict


DEFAULT_PRODUCTIVITY = {
    "fp": 8.0,
    "ucp": 20.0,
    "loc": 0.05,
}


def calculate_estimate(payload: Dict) -> Dict:
    metric_type = str(payload.get("metric_type", "fp")).lower()
    metric_value = _positive_float(payload.get("metric_value", 0), "度量值")
    productivity = float(payload.get("productivity") or DEFAULT_PRODUCTIVITY.get(metric_type, 8.0))
    hours_per_person_month = float(payload.get("hours_per_person_month") or 160)
    cost_per_person_month = float(payload.get("cost_per_person_month") or 12000)
    team_size = max(int(payload.get("team_size") or 1), 1)

    effort_hours = metric_value * productivity
    effort_person_months = effort_hours / hours_per_person_month
    cost = effort_person_months * cost_per_person_month
    duration_months = effort_person_months / team_size
    recommended_people = max(round(effort_person_months / max(float(payload.get("target_months") or duration_months or 1), 0.1)), 1)

    return {
        "metric_type": metric_type,
        "metric_value": round(metric_value, 4),
        "productivity": round(productivity, 4),
        "effort_hours": round(effort_hours, 4),
        "effort_person_months": round(effort_person_months, 4),
        "hours_per_person_month": round(hours_per_person_month, 4),
        "cost_per_person_month": round(cost_per_person_month, 4),
        "cost": round(cost, 4),
        "team_size": team_size,
        "duration_months": round(duration_months, 4),
        "recommended_people": recommended_people,
    }


def _positive_float(value, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    if number < 0:
        raise ValueError(f"{label}不能为负数")
    return number
