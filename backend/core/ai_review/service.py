from __future__ import annotations

from pathlib import Path

from core.project_metric import ProjectScanOptions, build_project_report_payload

from .context_builder import build_phase1_context, build_phase2_context
from .langchain_adapter import FixtureReviewer, LangChainReviewer, PayloadReviewer
from .source_selector import build_source_bundle, extract_focus_files


def run_ai_review(
    root_path: str,
    modules: list[str] | None = None,
    options: ProjectScanOptions | dict | None = None,
    *,
    model: str = "gpt-4.1-mini",
    function_point_payload: dict | None = None,
    estimate_payload: dict | None = None,
    reviewer=None,
    phase1_fixture: str = "",
    phase2_fixture: str = "",
    phase1_payload: dict | None = None,
    phase2_payload: dict | None = None,
) -> dict:
    review_agent = reviewer or create_reviewer(model, phase1_fixture, phase2_fixture, phase1_payload, phase2_payload)
    report_payload, bundle = build_project_report_payload(
        root_path,
        modules,
        options,
        function_point_payload=function_point_payload,
        estimate_payload=estimate_payload,
    )
    phase1_context = build_phase1_context(report_payload, bundle)
    phase1_result = review_agent.review_phase1(phase1_context)
    focus_files = extract_focus_files(phase1_result)
    source_bundle = build_source_bundle(Path(bundle["project"]["root"]), bundle["project"], bundle["complexity"], focus_files)
    phase2_context = build_phase2_context(phase1_result, source_bundle)
    phase2_result = review_agent.review_phase2(phase2_context)
    return {
        "project_path": bundle["project"]["root"],
        "model": model,
        "phase1_context": phase1_context,
        "phase2_context": phase2_context,
        "project_report": report_payload,
        "phase1": phase1_result,
        "phase2": phase2_result,
        "focus_files": focus_files,
        "source_bundle": source_bundle,
    }


def build_ai_review_report_payload(review_result: dict) -> dict:
    base_report = review_result.get("project_report", {})
    phase1 = review_result.get("phase1", {})
    phase2 = review_result.get("phase2", {})
    findings = phase1.get("findings", [])
    recommendations = phase2.get("recommendations", [])

    summary = dict(base_report.get("summary", {}))
    summary["AI 风险等级"] = phase1.get("summary", {}).get("risk_level", "unknown")
    summary["AI 重点文件数"] = len(review_result.get("focus_files", []))
    summary["AI 发现数"] = len(findings)
    summary["AI 建议数"] = len(recommendations)

    sections = list(base_report.get("sections", []))
    sections.append(
        {
            "heading": "AI 第一轮审查",
            "text": phase1.get("summary", {}).get("project_overview", "无"),
            "rows": findings or [{"severity": "-", "category": "-", "filename": "-", "reason": "无 AI 审查发现"}],
        }
    )
    sections.append(
        {
            "heading": "AI 改进建议",
            "text": f"建议优先级：{phase2.get('summary', {}).get('overall_priority', 'unknown')}",
            "rows": recommendations
            or [
                {
                    "priority": "-",
                    "filename": "-",
                    "problem": "-",
                    "suggestion": "无 AI 改进建议",
                    "expected_benefit": "-",
                    "evidence": [],
                    "target_symbols": [],
                    "refactor_steps": [],
                }
            ],
        }
    )
    return {
        "title": f"{base_report.get('title', 'SmartMetric 报告')} - AI 审查",
        "subtitle": "基于本地度量结果和源码片段的两阶段 AI 审查报告",
        "summary": summary,
        "sections": sections,
        "report_type": "ai_review",
    }


def create_reviewer(
    model: str,
    phase1_fixture: str = "",
    phase2_fixture: str = "",
    phase1_payload: dict | None = None,
    phase2_payload: dict | None = None,
):
    if phase1_payload and phase2_payload:
        return PayloadReviewer(phase1_payload, phase2_payload)
    if phase1_fixture and phase2_fixture:
        return FixtureReviewer(phase1_fixture, phase2_fixture)
    return LangChainReviewer(model=model)
