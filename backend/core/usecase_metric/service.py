from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from .calculator import factor_value, ucp_value, weighted_sum
from .defaults import ACTOR_WEIGHTS, EF_DEFAULT_FACTORS, TCF_DEFAULT_FACTORS, USE_CASE_WEIGHTS


def _normalized_counts(raw: Dict) -> Dict[str, int]:
    return {
        "simple": int(raw.get("simple", 0) or 0),
        "average": int(raw.get("average", 0) or 0),
        "complex": int(raw.get("complex", 0) or 0),
    }


def calculate_usecase_metrics(payload: Dict) -> Dict:
    use_case_counts = _normalized_counts(payload.get("use_case_counts", {}))
    actor_counts = _normalized_counts(payload.get("actor_counts", {}))

    tcf_factors: List[Dict] = payload.get("tcf_factors") or deepcopy(TCF_DEFAULT_FACTORS)
    ef_factors: List[Dict] = payload.get("ef_factors") or deepcopy(EF_DEFAULT_FACTORS)

    uuc = weighted_sum(use_case_counts, USE_CASE_WEIGHTS, "use_case_counts")
    uaw = weighted_sum(actor_counts, ACTOR_WEIGHTS, "actor_counts")

    tcf_sum, tcf = factor_value(tcf_factors, "TCF")
    ef_sum, ef = factor_value(ef_factors, "EF")
    ucp = ucp_value(uuc, uaw, tcf, ef)

    return {
        "use_case_counts": use_case_counts,
        "actor_counts": actor_counts,
        "uuc": uuc,
        "uaw": uaw,
        "tcf_sum": round(tcf_sum, 4),
        "tcf": round(tcf, 4),
        "ef_sum": round(ef_sum, 4),
        "ef": round(ef, 4),
        "ucp": round(ucp, 4),
        "tcf_factors": tcf_factors,
        "ef_factors": ef_factors,
    }


def parse_oom_and_suggest_counts(parsed: Dict) -> Dict:
    actors = parsed.get("actors", [])
    use_cases = parsed.get("use_cases", [])

    actor_counts = {"simple": 0, "average": 0, "complex": 0}
    for actor in actors:
        degree = int(actor.get("links", 0))
        if degree <= 1:
            actor_counts["simple"] += 1
        elif degree <= 3:
            actor_counts["average"] += 1
        else:
            actor_counts["complex"] += 1

    use_case_counts = {"simple": 0, "average": 0, "complex": 0}
    for uc in use_cases:
        tx = int(uc.get("transactions", uc.get("links", 0)))
        if tx <= 3:
            use_case_counts["simple"] += 1
        elif tx <= 7:
            use_case_counts["average"] += 1
        else:
            use_case_counts["complex"] += 1

    return {
        "actor_counts": actor_counts,
        "use_case_counts": use_case_counts,
        "actors": actors,
        "use_cases": use_cases,
        "metadata": parsed.get("metadata", {}),
    }
