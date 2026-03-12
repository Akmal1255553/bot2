from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiohttp

from config import Settings

from bot.services.ai.base import GenerationResult, ImageGenerationProvider
from bot.services.exceptions import ProviderError

logger = logging.getLogger(__name__)


class StabilityImageProvider(ImageGenerationProvider):
    GENERATE_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.stability_api_key:
            raise ProviderError("STABILITY_API_KEY is required for image generation")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.stability_api_key}",
            "Accept": "application/json",
        }

    async def generate(self, prompt: str, size: str, watermark: bool) -> GenerationResult:
        del size
        self._enforce_cost_guard()
        payload = self._build_payload(prompt=prompt, watermark=watermark)
        retries = max(self.settings.provider_timeout_retries, 0)
        timeout = aiohttp.ClientTimeout(total=self.settings.request_timeout_seconds)

        self._log_debug_request(prompt=prompt, watermark=watermark)

        for attempt in range(retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        self.GENERATE_URL,
                        headers=self.headers,
                        data=payload,
                    ) as response:
                        raw_text = await response.text()
                        self._log_debug_response(response.status, raw_text)

                        if response.status != 200:
                            detail = self._response_error_detail(raw_text)
                            if self._is_retryable_status(response.status) and attempt < retries:
                                await self._sleep_before_retry(
                                    attempt=attempt,
                                    reason=f"http_{response.status}",
                                )
                                payload = self._build_payload(prompt=prompt, watermark=watermark)
                                continue
                            raise ProviderError(
                                self._build_status_error_message(response.status, detail)
                            )

                        image_bytes = self._image_bytes_from_json(raw_text)
                        image_bytes = self._save_temp_and_reload(image_bytes)
                        return GenerationResult(
                            provider="stability-ai",
                            media_bytes=image_bytes,
                            mime_type="image/png",
                        )
            except (asyncio.TimeoutError, aiohttp.ServerTimeoutError):
                if attempt < retries:
                    await self._sleep_before_retry(attempt=attempt, reason="timeout")
                    payload = self._build_payload(prompt=prompt, watermark=watermark)
                    continue
                raise ProviderError("Stability API timed out. Please try again.")
            except (aiohttp.ClientConnectionError, aiohttp.ClientPayloadError) as exc:
                if attempt < retries:
                    await self._sleep_before_retry(attempt=attempt, reason=exc.__class__.__name__)
                    payload = self._build_payload(prompt=prompt, watermark=watermark)
                    continue
                raise ProviderError(f"Stability network error: {exc}") from exc
            except aiohttp.ClientError as exc:
                raise ProviderError(f"Stability network error: {exc}") from exc

        raise ProviderError("Stability provider failed without a response")

    async def _sleep_before_retry(self, attempt: int, reason: str) -> None:
        delay = 1.5 * (attempt + 1)
        logger.warning(
            "stability_retry_scheduled",
            extra={"attempt": attempt + 1, "delay_seconds": delay, "reason": reason},
        )
        await asyncio.sleep(delay)

    def _is_retryable_status(self, status: int) -> bool:
        return status == 429 or 500 <= status < 600

    def _response_error_detail(self, raw_text: str) -> str:
        data = self._parse_json(raw_text)
        if isinstance(data, dict):
            errors = data.get("errors")
            if isinstance(errors, list) and errors:
                return "; ".join(str(item) for item in errors[:2])
            if data.get("message"):
                return str(data["message"])
            if data.get("name"):
                return str(data["name"])
        if raw_text:
            return raw_text[:240]
        return "unknown error"

    def _build_status_error_message(self, status: int, detail: str) -> str:
        if status == 401:
            return f"Stability API error 401 Unauthorized: invalid STABILITY_API_KEY. {detail}"
        if status == 402:
            return f"Stability API error 402 Payment Required: no active billing. {detail}"
        if status == 429:
            return f"Stability API error 429 Rate limit: too many requests. {detail}"
        if 400 <= status < 600:
            return f"Stability API error {status}: {detail}"
        return f"Stability provider failed with unexpected status {status}: {detail}"

    def _image_bytes_from_json(self, raw_text: str) -> bytes:
        data = self._parse_json(raw_text)
        if not isinstance(data, dict):
            raise ProviderError("Stability API response is not valid JSON")
        image_base64 = data.get("image")
        if not image_base64 or not isinstance(image_base64, str):
            raise ProviderError("Stability API response did not include base64 image data")
        try:
            return base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ProviderError("Failed to decode base64 image from Stability API") from exc

    def _save_temp_and_reload(self, image_bytes: bytes) -> bytes:
        temp_path: Path | None = None
        try:
            with NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)
                tmp_file.write(image_bytes)
            return temp_path.read_bytes()
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def _parse_json(self, raw_text: str) -> dict[str, object] | list[object] | None:
        if not raw_text:
            return None
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return None

    def _build_payload(self, prompt: str, watermark: bool) -> aiohttp.FormData:
        output_format = "png"

        effective_prompt = prompt
        if watermark:
            effective_prompt = (
                f"{prompt}. Add small visible watermark text 'FREE TIER' in bottom-right corner."
            )

        form = aiohttp.FormData(default_to_multipart=True)
        form.add_field("prompt", effective_prompt)
        form.add_field("output_format", output_format)
        return form

    def _enforce_cost_guard(self) -> None:
        max_cost = self.settings.stability_max_image_cost_usd
        cost = self._estimated_cost_usd()
        if cost > max_cost:
            raise ProviderError(
                f"Pricing guard blocked generation: estimated cost ${cost:.4f} exceeds "
                f"${max_cost:.4f} limit."
            )

    def _estimated_cost_usd(self) -> float:
        return self.settings.stability_core_credits * self.settings.stability_credit_price_usd

    def _log_debug_request(self, prompt: str, watermark: bool) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "stability_generate_request",
                extra={
                    "url": self.GENERATE_URL,
                    "prompt_length": len(prompt),
                    "watermark": watermark,
                    "output_format": "png",
                },
            )

    def _log_debug_response(self, status: int, raw_text: str) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "stability_generate_response",
                extra={
                    "status": status,
                    "body_preview": (raw_text or "")[:300],
                },
            )
