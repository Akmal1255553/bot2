from __future__ import annotations

import re

from aiogram.types import Message

URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
HTML_RE = re.compile(r"<[^>]+>")


def sanitize_prompt(message: Message, max_len: int, banned_words: set[str]) -> str | None:
    if not message.text:
        return None

    prompt = " ".join(message.text.split()).strip()
    if not prompt or len(prompt) > max_len:
        return None
    if URL_RE.search(prompt):
        return None
    if HTML_RE.search(prompt):
        return None

    lowered = prompt.lower()
    for word in banned_words:
        if word and word in lowered:
            return None

    return prompt
