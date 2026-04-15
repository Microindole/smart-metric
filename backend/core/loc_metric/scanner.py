from __future__ import annotations

from .language_rules import C_STYLE_LANGS


def _scan_c_style(text: str) -> dict:
    total = blank = comment = code = 0
    in_block = False

    for raw in text.splitlines():
        total += 1
        line = raw.rstrip("\n")
        if not line.strip():
            blank += 1
            continue

        i = 0
        has_code = False
        has_comment = False

        while i < len(line):
            if in_block:
                has_comment = True
                end = line.find("*/", i)
                if end == -1:
                    i = len(line)
                    break
                in_block = False
                i = end + 2
                continue

            if line.startswith("//", i):
                has_comment = True
                break

            if line.startswith("/*", i):
                has_comment = True
                in_block = True
                i += 2
                continue

            if not line[i].isspace():
                has_code = True
            i += 1

        if has_code:
            code += 1
        elif has_comment:
            comment += 1
        else:
            blank += 1

    return {
        "total_lines": total,
        "blank_lines": blank,
        "comment_lines": comment,
        "code_lines": code,
    }


def _scan_python(text: str) -> dict:
    total = blank = comment = code = 0
    in_doc = False
    doc_delim = None

    for raw in text.splitlines():
        total += 1
        line = raw.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            blank += 1
            continue

        if in_doc:
            comment += 1
            if doc_delim and doc_delim in stripped:
                in_doc = False
                doc_delim = None
            continue

        if stripped.startswith("#"):
            comment += 1
            continue

        if stripped.startswith("'''") or stripped.startswith('"""'):
            delim = stripped[:3]
            if stripped.count(delim) >= 2 and len(stripped) > 5:
                comment += 1
                continue
            in_doc = True
            doc_delim = delim
            comment += 1
            continue

        code += 1

    return {
        "total_lines": total,
        "blank_lines": blank,
        "comment_lines": comment,
        "code_lines": code,
    }


def scan_lines(text: str, language: str) -> dict:
    if language in C_STYLE_LANGS:
        return _scan_c_style(text)
    if language == "python":
        return _scan_python(text)
    raise ValueError(f"暂不支持语言: {language}")
