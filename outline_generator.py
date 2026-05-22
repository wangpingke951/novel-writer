import json
import os
import re
from datetime import datetime
from llm_client import LLMClient
from prompts.outline import (
    CLASSIFY_PROMPT,
    REVISION_PROMPT,
    SYSTEM_PROMPT,
    classify_user_prompt,
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

    def revise(self, original_outline: str, feedback: str) -> str:
        messages = [
            {"role": "system", "content": REVISION_PROMPT},
            {"role": "user", "content": revision_user_prompt(original_outline, feedback)},
        ]

        result = self._client.chat_completion(messages)
        return result

    def generate(self, genre: str, style: str, premise: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt(genre, style, premise)},
        ]

        result = self._client.chat_completion(messages)
        return result

    def save(self, content: str, output_dir: str = "output") -> str:
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outline_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return os.path.abspath(filepath)
