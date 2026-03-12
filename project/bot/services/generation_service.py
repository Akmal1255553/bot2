from __future__ import annotations

import asyncio

from database.models import Plan

from bot.services.ai.base import GenerationResult, ImageGenerationProvider
from bot.services.exceptions import ProviderError

ASPECT_RATIO_SIZES = {
    "1:1": "1024x1024",
    "9:16": "768x1344",
    "16:9": "1344x768",
}


class GenerationService:
    def __init__(self, image_provider: ImageGenerationProvider) -> None:
        self.image_provider = image_provider

    def generation_params(self, plan: Plan, aspect_ratio: str = "1:1") -> tuple[str, bool]:
        size = ASPECT_RATIO_SIZES.get(aspect_ratio, "1024x1024")
        watermark = plan == Plan.FREE
        return size, watermark

    async def generate_image(
        self, prompt: str, plan: Plan, aspect_ratio: str = "1:1"
    ) -> GenerationResult:
        size, watermark = self.generation_params(plan, aspect_ratio)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                return await self.image_provider.generate(prompt=prompt, size=size, watermark=watermark)
            except Exception as exc:
                last_error = exc
                err = str(exc).lower()
                is_retryable = any(word in err for word in ("429", "throttled", "timeout", "temporarily"))
                if attempt < 2 and is_retryable:
                    await asyncio.sleep(2.5 * (attempt + 1))
                    continue
                break
        raise ProviderError(f"Image provider failed: {last_error}")
