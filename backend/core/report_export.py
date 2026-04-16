from __future__ import annotations

import html
from typing import Iterable


def export_report(payload: dict, fmt: str) -> bytes:
    normalized = fmt.lower()
    if normalized == "markdown":
        return build_markdown_report(payload).encode("utf-8")
    if normalized == "html":
        return build_html_report(payload).encode("utf-8")
    if normalized == "pdf":
        return build_pdf_report(payload)
    raise ValueError(f"暂不支持的报告导出格式: {fmt}")


def build_markdown_report(payload: dict) -> str:
    title = payload.get("title", "SmartMetric 报告")
    subtitle = payload.get("subtitle", "")
    summary = payload.get("summary", {})
    sections = payload.get("sections", [])

    lines = [f"# {title}"]
    if subtitle:
        lines.extend(["", subtitle])

    if summary:
        lines.extend(["", "## Summary", ""])
        for key, value in summary.items():
            lines.append(f"- **{key}**: {value}")

    for section in sections:
        heading = section.get("heading", "Section")
        lines.extend(["", f"## {heading}"])
        body = section.get("text", "")
        if body:
            lines.extend(["", body])
        rows = section.get("rows", [])
        if rows:
            headers = list(rows[0].keys())
            lines.extend(["", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"])
            for row in rows:
                lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines) + "\n"


def build_html_report(payload: dict) -> str:
    title = html.escape(str(payload.get("title", "SmartMetric 报告")))
    subtitle = html.escape(str(payload.get("subtitle", "")))
    summary = payload.get("summary", {})
    sections = payload.get("sections", [])

    parts = [
        "<!DOCTYPE html>",
        "<html lang='zh-CN'>",
        "<head>",
        "  <meta charset='utf-8' />",
        f"  <title>{title}</title>",
        "  <style>",
        "    body { font-family: Arial, 'Microsoft YaHei', sans-serif; margin: 32px; color: #1f2937; }",
        "    h1, h2 { color: #102a43; }",
        "    table { border-collapse: collapse; width: 100%; margin: 12px 0 20px; }",
        "    th, td { border: 1px solid #dbe2ea; padding: 8px 10px; text-align: left; }",
        "    th { background: #f3f6fb; }",
        "    .summary li { margin: 6px 0; }",
        "  </style>",
        "</head>",
        "<body>",
        f"  <h1>{title}</h1>",
    ]
    if subtitle:
        parts.append(f"  <p>{subtitle}</p>")

    if summary:
        parts.extend(["  <h2>Summary</h2>", "  <ul class='summary'>"])
        for key, value in summary.items():
            parts.append(f"    <li><strong>{html.escape(str(key))}</strong>: {html.escape(str(value))}</li>")
        parts.append("  </ul>")

    for section in sections:
        heading = html.escape(str(section.get("heading", "Section")))
        parts.append(f"  <h2>{heading}</h2>")
        text = section.get("text", "")
        if text:
            parts.append(f"  <p>{html.escape(str(text))}</p>")
        rows = section.get("rows", [])
        if rows:
            headers = list(rows[0].keys())
            parts.append("  <table><thead><tr>")
            for header in headers:
                parts.append(f"    <th>{html.escape(str(header))}</th>")
            parts.append("  </tr></thead><tbody>")
            for row in rows:
                parts.append("  <tr>")
                for header in headers:
                    parts.append(f"    <td>{html.escape(str(row.get(header, '')))}</td>")
                parts.append("  </tr>")
            parts.append("  </tbody></table>")

    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def build_pdf_report(payload: dict) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.pdfmetrics import registerFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PDF 导出依赖未安装，请执行 pip install -r backend\\requirements.txt") from exc

    import io

    registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ZhTitle", parent=styles["Title"], fontName="STSong-Light")
    heading_style = ParagraphStyle("ZhHeading", parent=styles["Heading2"], fontName="STSong-Light")
    body_style = ParagraphStyle("ZhBody", parent=styles["BodyText"], fontName="STSong-Light", leading=18)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    story = [Paragraph(str(payload.get("title", "SmartMetric 报告")), title_style), Spacer(1, 8)]

    subtitle = payload.get("subtitle", "")
    if subtitle:
        story.extend([Paragraph(str(subtitle), body_style), Spacer(1, 8)])

    summary = payload.get("summary", {})
    if summary:
        story.extend([Paragraph("Summary", heading_style), Spacer(1, 4)])
        for key, value in summary.items():
            story.append(Paragraph(f"{key}: {value}", body_style))
        story.append(Spacer(1, 8))

    for section in payload.get("sections", []):
        story.extend([Paragraph(str(section.get("heading", "Section")), heading_style), Spacer(1, 4)])
        text = section.get("text", "")
        if text:
            story.extend([Paragraph(str(text), body_style), Spacer(1, 4)])
        rows = section.get("rows", [])
        if rows:
            headers = list(rows[0].keys())
            table_data = [headers] + [[str(row.get(header, "")) for header in headers] for row in rows]
            table = Table(table_data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f6fb")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbe2ea")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ]
                )
            )
            story.extend([table, Spacer(1, 8)])

    doc.build(story)
    return buffer.getvalue()
