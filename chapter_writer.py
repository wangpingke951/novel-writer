import os
import re
from collections.abc import Callable
from llm_client import LLMClient
from prompts.chapter import (
    CHAPTER_REVISION_PROMPT,
    CHAPTER_SYSTEM_PROMPT,
    chapter_revision_user_prompt,
    chapter_user_prompt,
)

_CN_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_TENS = {"十": 10, "百": 100, "千": 1000}


def _parse_chapter_number(raw: str) -> int:
    """Parse chapter number from Chinese or Arabic numeral. 三十八 -> 38, 5 -> 5."""
    try:
        return int(raw)
    except ValueError:
        pass

    total = 0
    current = 0
    for ch in raw:
        if ch in _CN_DIGITS:
            current = _CN_DIGITS[ch]
        elif ch in _CN_TENS:
            unit = _CN_TENS[ch]
            total += (current or 1) * unit
            current = 0
    total += current
    return total


class ChapterWriter:
    def __init__(self, client: LLMClient | None = None):
        self._client = client or LLMClient()

    def parse_outline(self, outline_text: str) -> list[dict]:
        """Parse outline Markdown into structured chapter list.

        Supports both Arabic (第1章) and Chinese (第一章) numerals.
        """
        chapters: list[dict] = []
        current_volume = ""

        lines = outline_text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            vol_match = re.match(r"^## (.+)$", line)
            if vol_match:
                current_volume = vol_match.group(1)
                continue

            ch_match = re.match(r"^### 第(.+?)章 (.+)$", line)
            if ch_match:
                ch_num = _parse_chapter_number(ch_match.group(1))
                ch_title = ch_match.group(2)
                summary = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    quote_match = re.match(r"^>\s?(.+)$", next_line)
                    if quote_match:
                        summary = quote_match.group(1)

                chapters.append({
                    "volume": current_volume,
                    "number": ch_num,
                    "title": ch_title,
                    "summary": summary,
                })

        return chapters

    def _stream_accumulate(
        self,
        messages: list[dict],
        on_chunk: Callable[[str], None] | None = None,
        **kwargs,
    ) -> str:
        chunks: list[str] = []
        for chunk in self._client.chat_completion_stream(
            messages, on_chunk=on_chunk, **kwargs
        ):
            chunks.append(chunk)
        return "".join(chunks)

    def write_chapter(
        self,
        outline_text: str,
        chapter: dict,
        prev_chapter_text: str = "",
        on_chunk: Callable[[str], None] | None = None,
    ) -> str:
        """Write a single chapter based on outline and previous chapter."""
        messages = [
            {"role": "system", "content": CHAPTER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": chapter_user_prompt(
                    outline_text, chapter, prev_chapter_text
                ),
            },
        ]

        return self._stream_accumulate(messages, on_chunk=on_chunk)

    def revise_chapter(
        self,
        chapter_text: str,
        chapter: dict,
        feedback: str,
        on_chunk: Callable[[str], None] | None = None,
    ) -> str:
        """Revise a chapter based on user feedback."""
        messages = [
            {"role": "system", "content": CHAPTER_REVISION_PROMPT},
            {
                "role": "user",
                "content": chapter_revision_user_prompt(
                    chapter_text, chapter, feedback
                ),
            },
        ]

        return self._stream_accumulate(messages, on_chunk=on_chunk)

    def save(
        self, content: str, chapter: dict, output_dir: str = "output/chapters"
    ) -> str:
        """Save chapter content to file."""
        os.makedirs(output_dir, exist_ok=True)

        ch_num = chapter["number"]
        # Sanitize title for filename
        safe_title = re.sub(r'[\\/*?:"<>|]', "", chapter.get("title", ""))
        filename = f"ch{ch_num:04d}_{safe_title}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return os.path.abspath(filepath)
