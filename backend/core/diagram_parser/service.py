from __future__ import annotations

from .adapters import DefaultOomAdapter


ADAPTERS = [DefaultOomAdapter()]


def parse_usecase_diagram(filename: str, content: bytes) -> dict:
    for adapter in ADAPTERS:
        if adapter.can_handle(filename, content):
            return adapter.parse(content)
    raise ValueError("未找到可处理该文件的图解析适配器")
