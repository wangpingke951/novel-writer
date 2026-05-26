import json
import os
import re
from collections.abc import Callable
from datetime import datetime
from llm_client import LLMClient
from prompts.outline import (
    CLASSIFY_PROMPT,
    IDEA_GENERATION_PROMPT,
    REVISION_PROMPT,
    SYSTEM_PROMPT,
    classify_user_prompt,
    ideas_user_prompt,
    revision_user_prompt,
    user_prompt,
)


class OutlineGenerator:
    def __init__(self, client: LLMClient | None = None):
        self._client = client or LLMClient()

    def classify(self, premise: str) -> dict[str, str]:
        messages = [
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": classify_user_prompt(premise)},
        ]

        result = self._client.chat_completion(messages, temperature=0.3)

        match = re.search(r"\{[\s\S]*\}", result.strip())
        if match:
            return json.loads(match.group(0))
        return {"genre": "玄幻", "style": "热血升级流", "title": ""}

    def _stream_accumulate(self, messages: list[dict], on_chunk: Callable[[str], None] | None = None, **kwargs) -> str:
        """Stream LLM response, calling on_chunk for each fragment, returning full text."""
        chunks: list[str] = []
        for chunk in self._client.chat_completion_stream(messages, on_chunk=on_chunk, **kwargs):
            chunks.append(chunk)
        return "".join(chunks)

    def revise(self, original_outline: str, feedback: str, on_chunk: Callable[[str], None] | None = None) -> str:
        messages = [
            {"role": "system", "content": REVISION_PROMPT},
            {"role": "user", "content": revision_user_prompt(original_outline, feedback)},
        ]

        return self._stream_accumulate(messages, on_chunk=on_chunk)

    def generate_ideas(self, premise: str, on_chunk: Callable[[str], None] | None = None) -> list[dict]:
        """基于创意生成 3-5 个不同的故事方向。"""
        messages = [
            {"role": "system", "content": IDEA_GENERATION_PROMPT},
            {"role": "user", "content": ideas_user_prompt(premise)},
        ]

        result = self._stream_accumulate(messages, on_chunk=on_chunk, temperature=0.8, thinking="disabled")

        match = re.search(r"\{[\s\S]*\}", result.strip())
        if match:
            try:
                data = json.loads(match.group(0))
                ideas = data.get("ideas", [])
                required = {"title", "genre", "style", "hook", "summary"}
                return [idea for idea in ideas if required.issubset(idea.keys())]
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def generate(self, premise: str, selected_idea: dict, on_chunk: Callable[[str], None] | None = None) -> str:
        """基于选定故事方向生成详细大纲。"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(premise, selected_idea)},
        ]

        return self._stream_accumulate(messages, on_chunk=on_chunk)

    def save(self, content: str, output_dir: str = "output", title_hint: str = "") -> str:
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{title_hint}_" if title_hint else ""
        filename = f"outline_{prefix}{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return os.path.abspath(filepath)
