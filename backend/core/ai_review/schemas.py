from __future__ import annotations


PHASE1_SCHEMA = {
    "summary": {
        "risk_level": "low|medium|high",
        "project_overview": "string",
    },
    "focus_files": ["relative/path.py"],
    "findings": [
        {
            "id": "F1",
            "severity": "low|medium|high",
            "category": "complexity|dependency|design|oo|testing|maintainability",
            "filename": "relative/path.py",
            "reason": "string",
            "need_source": True,
        }
    ],
}


PHASE2_SCHEMA = {
    "summary": {
        "overall_priority": "low|medium|high",
        "refactor_order": ["relative/path.py"],
    },
    "recommendations": [
        {
            "finding_id": "F1",
            "filename": "relative/path.py",
            "priority": "low|medium|high",
            "problem": "string",
            "evidence": ["string"],
            "target_symbols": ["function_or_class_name"],
            "suggestion": "string",
            "refactor_steps": ["string"],
            "expected_benefit": "string",
            "refactor_scope": "small|medium|large",
        }
    ],
}
