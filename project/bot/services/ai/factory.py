from config import get_settings

from bot.services.ai.base import ImageGenerationProvider
from bot.services.ai.stability_provider import StabilityImageProvider


def get_image_provider() -> ImageGenerationProvider:
    settings = get_settings()
    return StabilityImageProvider(settings)
