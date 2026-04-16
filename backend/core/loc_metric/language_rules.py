LANGUAGE_ALIASES = {
    ".java": "java",
    ".c": "c",
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".h": "cpp",
}

C_STYLE_LANGS = {"java", "cpp", "c", "javascript"}


def detect_language(filename: str, specified: str | None = None) -> str:
    if specified:
        return specified.lower().strip()

    lower = filename.lower()
    for ext, lang in LANGUAGE_ALIASES.items():
        if lower.endswith(ext):
            return lang
    raise ValueError(f"不支持的文件类型: {filename}")
