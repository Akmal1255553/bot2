from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, ratio_label, style_label, t
from bot.keyboards.common import language_selection_keyboard
from bot.keyboards.generation import (
    STYLE_PROMPTS,
    aspect_ratio_keyboard,
    style_picker_keyboard,
)
from bot.services.exceptions import AccessDeniedError, ProviderError
from bot.services.generation_guard import GenerationGuard
from bot.services.generation_service import GenerationService
from bot.states import GenerationStates
from bot.utils.formatters import format_generation_caption
from bot.utils.validators import sanitize_prompt

router = Router()
logger = logging.getLogger(__name__)


def _localized_access_error(language: str, exc: AccessDeniedError) -> str:
    code = getattr(exc, "code", "error.access_denied")
    context = getattr(exc, "context", {})
    return t(language, code, **context)


@router.message(Command("generate_image"))
async def cmd_generate_image(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)

    if not user.language:
        guessed_language = normalize_language(message.from_user.language_code)
        await message.answer(
            t(guessed_language, "app.language_prompt"),
            reply_markup=language_selection_keyboard(),
        )
        return

    language = normalize_language(user.language or message.from_user.language_code)
    await state.set_state(GenerationStates.choosing_style)
    await message.answer(
        t(language, "generation.choose_style"),
        reply_markup=style_picker_keyboard(language),
    )


@router.callback_query(GenerationStates.choosing_style, F.data.startswith("style:"))
async def callback_choose_style(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not query.message or not query.data or not query.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)

    style = query.data.split("style:", maxsplit=1)[1]
    await state.update_data(style=style)
    await state.set_state(GenerationStates.choosing_aspect_ratio)
    await query.message.answer(
        t(language, "generation.choose_ratio"),
        reply_markup=aspect_ratio_keyboard(language),
    )
    await query.answer()


@router.callback_query(GenerationStates.choosing_aspect_ratio, F.data.startswith("ratio:"))
async def callback_choose_ratio(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not query.message or not query.data or not query.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)

    ratio = query.data.split("ratio:", maxsplit=1)[1]
    await state.update_data(aspect_ratio=ratio)
    await state.set_state(GenerationStates.waiting_for_image_prompt)
    await query.message.answer(t(language, "generation.send_prompt"))
    await query.answer()


@router.message(GenerationStates.waiting_for_image_prompt, F.text)
async def process_image_prompt(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    generation_service: GenerationService,
    generation_guard: GenerationGuard,
    settings: Settings,
) -> None:
    if not message.from_user:
        return

    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)

    if not user.language:
        guessed_language = normalize_language(message.from_user.language_code)
        await message.answer(
            t(guessed_language, "app.language_prompt"),
            reply_markup=language_selection_keyboard(),
        )
        await state.clear()
        return

    language = normalize_language(user.language or message.from_user.language_code)
    prompt = sanitize_prompt(message, settings.generation_max_prompt_len, settings.banned_words)
    if not prompt:
        await message.answer(t(language, "generation.invalid_prompt"))
        return

    fsm_data = await state.get_data()
    style = fsm_data.get("style", "none")
    aspect_ratio = fsm_data.get("aspect_ratio", "1:1")

    short_prompt = prompt[:80] + ("..." if len(prompt) > 80 else "")
    progress_msg = await message.answer(
        t(
            language,
            "generation.progress",
            style=style_label(language, style),
            ratio=ratio_label(language, aspect_ratio),
            prompt=short_prompt,
        )
    )

    try:
        await services.subscription_service.ensure_request_limit(user)
        await services.subscription_service.ensure_can_generate_image(user)
        await generation_guard.ensure_user_rate_limit(user.telegram_id)
        await generation_guard.ensure_global_rate_limit()
        await generation_guard.ensure_daily_capacity()

        logger.info(
            "generation_cost_log",
            extra={
                "user_id": user.telegram_id,
                "prompt_length": len(prompt),
                "style": style,
                "aspect_ratio": aspect_ratio,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "plan": user.plan.value,
            },
        )

        style_prefix = STYLE_PROMPTS.get(style, "")
        full_prompt = f"{style_prefix}, {prompt}" if style_prefix else prompt

        async with generation_guard.acquire(user.plan):
            async with ChatActionSender.upload_photo(message.chat.id, bot=message.bot):
                result = await generation_service.generate_image(
                    full_prompt,
                    user.plan,
                    aspect_ratio=aspect_ratio,
                )

        await services.subscription_service.consume_image_generation(user)
        queue_name = {"FREE": "low", "BASIC": "medium", "PRO": "high"}.get(
            user.plan.value,
            "low",
        )

        image_url = result.media_url or ""
        await services.history_repo.save_generation(
            user_id=user.id,
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
            plan=user.plan.value,
        )

        try:
            await progress_msg.delete()
        except Exception:
            pass

        image_payload: str | BufferedInputFile
        if result.media_url:
            image_payload = result.media_url
        elif result.media_bytes:
            ext = "png"
            if result.mime_type == "image/jpeg":
                ext = "jpg"
            elif result.mime_type == "image/webp":
                ext = "webp"
            image_payload = BufferedInputFile(result.media_bytes, filename=f"result.{ext}")
        else:
            raise ProviderError("Image provider returned an empty result")

        caption = format_generation_caption(
            user=user,
            style=style,
            aspect_ratio=aspect_ratio,
            queue_name=queue_name,
            language=language,
        )
        await message.answer_photo(image_payload, caption=caption)

    except AccessDeniedError as exc:
        localized = _localized_access_error(language, exc)
        try:
            await progress_msg.edit_text(localized)
        except Exception:
            await message.answer(localized)
    except ProviderError as exc:
        logger.exception("image_generation_provider_error")
        err = str(exc).lower()
        if "429" in err or "throttled" in err:
            key = "error.provider_rate_limited"
        elif "pricing guard" in err or "cost" in err:
            key = "error.provider_cost_guard"
        elif "402" in err or "payment method" in err:
            key = "error.provider_billing"
        elif "timed out" in err or "timeout" in err:
            key = "error.provider_timeout"
        else:
            key = "error.provider_unavailable"

        text = t(language, key)
        try:
            await progress_msg.edit_text(text)
        except Exception:
            await message.answer(text)
    except Exception:
        logger.exception("image_generation_unexpected_error")
        text = t(language, "error.unexpected")
        try:
            await progress_msg.edit_text(text)
        except Exception:
            await message.answer(text)
    finally:
        await state.clear()


@router.message(GenerationStates.waiting_for_image_prompt)
async def invalid_prompt_type(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        await message.answer(t("en", "generation.invalid_prompt_type"))
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(user.language or message.from_user.language_code)
    await message.answer(t(language, "generation.invalid_prompt_type"))
