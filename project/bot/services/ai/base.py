from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class GenerationResult:
    provider: str
    media_url: str | None = None
    media_bytes: bytes | None = None
    mime_type: str | None = None


class ImageGenerationProvider(Protocol):
    async def generate(self, prompt: str, size: str, watermark: bool) -> GenerationResult:
        raise NotImplementedError
