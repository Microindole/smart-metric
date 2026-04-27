from __future__ import annotations

import json
import re
from pathlib import Path

from .config import load_ai_review_config
from .prompting import build_phase1_variables, build_phase2_variables, load_prompt


JSON_BLOCK_PATTERN = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


class BaseReviewer:
    def review_phase1(self, context_text: str) -> dict:
        raise NotImplementedError

    def review_phase2(self, review_context: str) -> dict:
        raise NotImplementedError


class FixtureReviewer(BaseReviewer):
    def __init__(self, phase1_file: str, phase2_file: str):
        self.phase1_file = Path(phase1_file)
        self.phase2_file = Path(phase2_file)

    def review_phase1(self, context_text: str) -> dict:
        return json.loads(self.phase1_file.read_text(encoding="utf-8"))

    def review_phase2(self, review_context: str) -> dict:
        return json.loads(self.phase2_file.read_text(encoding="utf-8"))


class PayloadReviewer(BaseReviewer):
    def __init__(self, phase1_payload: dict, phase2_payload: dict):
        self.phase1_payload = phase1_payload
        self.phase2_payload = phase2_payload

    def review_phase1(self, context_text: str) -> dict:
        return self.phase1_payload

    def review_phase2(self, review_context: str) -> dict:
        return self.phase2_payload


class LangChainReviewer(BaseReviewer):
    def __init__(self, model: str = "gpt-4.1-mini", temperature: float = 0.0):
        config = load_ai_review_config()
        planner = config.get("planner", {})
        self.model = model or planner.get("model", "gpt-4.1-mini")
        self.temperature = temperature
        self.api_key = planner.get("apiKey", "")
        self.api_base = planner.get("apiBase", "")

    def review_phase1(self, context_text: str) -> dict:
        return self._invoke(
            load_prompt("phase1_system.txt"),
            load_prompt("phase1_user.txt"),
            build_phase1_variables(context_text),
        )

    def review_phase2(self, review_context: str) -> dict:
        return self._invoke(
            load_prompt("phase2_system.txt"),
            load_prompt("phase2_user.txt"),
            build_phase2_variables(review_context),
        )

    def _invoke(self, system_prompt: str, user_prompt: str, variables: dict) -> dict:
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("未安装 LangChain 依赖，请执行 pip install -r backend\\requirements.txt") from exc

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )
        kwargs = {"model": self.model, "temperature": self.temperature}
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["base_url"] = self.api_base
        model = ChatOpenAI(**kwargs)
        chain = prompt | model
        response = chain.invoke(variables)
        content = getattr(response, "content", "") or ""
        return parse_json_response(content)


def parse_json_response(content: str) -> dict:
    text = str(content or "").strip()
    if not text:
        return {}
    fenced = JSON_BLOCK_PATTERN.search(text)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError("AI 返回内容不是有效 JSON")
