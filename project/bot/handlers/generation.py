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
from bot.keyboards.common import subscription_offer_keyboard
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


# --- Step 1: /generate_image → show style picker ---

@router.message(Command("generate_image"))
async def cmd_generate_image(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.from_user:
        return
    services = build_services(session)
    await services.user_service.get_or_create(message.from_user.id)
    await state.set_state(GenerationStates.choosing_style)
    await message.answer(
        "🎨 <b>Choose an art style:</b>",
        reply_markup=style_picker_keyboard(),
    )


# --- Step 2: style chosen → show aspect ratio picker ---

@router.callback_query(GenerationStates.choosing_style, F.data.startswith("style:"))
async def callback_choose_style(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message or not query.data:
        return
    style = query.data.split("style:", maxsplit=1)[1]
    await state.update_data(style=style)
    await state.set_state(GenerationStates.choosing_aspect_ratio)
    await query.message.answer(
        "📐 <b>Choose aspect ratio:</b>",
        reply_markup=aspect_ratio_keyboard(),
    )
    await query.answer()


# --- Step 3: ratio chosen → ask for prompt ---

@router.callback_query(GenerationStates.choosing_aspect_ratio, F.data.startswith("ratio:"))
async def callback_choose_ratio(query: CallbackQuery, state: FSMContext) -> None:
    if not query.message or not query.data:
        return
    ratio = query.data.split("ratio:", maxsplit=1)[1]
    await state.update_data(aspect_ratio=ratio)
    await state.set_state(GenerationStates.waiting_for_image_prompt)
    await query.message.answer(
        "💬 <b>Send your prompt</b> (max 350 chars, text only)."
    )
    await query.answer()


# --- Step 4: prompt received → generate image ---

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

    prompt = sanitize_prompt(message, settings.generation_max_prompt_len, settings.banned_words)
    if not prompt:
        await message.answer(
            "⚠️ Invalid prompt. Remove URLs/HTML/blocked words and keep under 350 chars."
        )
        return

    fsm_data = await state.get_data()
    style = fsm_data.get("style", "none")
    aspect_ratio = fsm_data.get("aspect_ratio", "1:1")

    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)

    # Send progress message
    progress_msg = await message.answer(
        "⏳ <b>Generating your image...</b>\n\n"
        f"🎨 Style: {style}\n"
        f"📐 Ratio: {aspect_ratio}\n"
        f"💬 Prompt: <i>{prompt[:80]}{'…' if len(prompt) > 80 else ''}</i>"
    )

    try:
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

        # Prepend style to prompt
        style_prefix = STYLE_PROMPTS.get(style, "")
        full_prompt = f"{style_prefix}, {prompt}" if style_prefix else prompt

        async with generation_guard.acquire(user.plan):
            async with ChatActionSender.upload_photo(message.chat.id, bot=message.bot):
                result = await generation_service.generate_image(
                    full_prompt, user.plan, aspect_ratio=aspect_ratio
                )

        await services.subscription_service.consume_image_generation(user)
        queue_name = {"FREE": "low", "BASIC": "medium", "PRO": "high"}.get(
            user.plan.value, "low"
        )

        # Save to history
        image_url = result.media_url or ""
        await services.history_repo.save_generation(
            user_id=user.id,
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
            plan=user.plan.value,
        )

        # Delete progress message
        try:
            await progress_msg.delete()
        except Exception:
            pass

        # Build the photo payload
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

        caption = format_generation_caption(user, style, aspect_ratio, queue_name)
        await message.answer_photo(image_payload, caption=caption)

    except AccessDeniedError as exc:
        try:
            await progress_msg.edit_text(f"⛔ {exc}")
        except Exception:
            await message.answer(str(exc), reply_markup=subscription_offer_keyboard())
    except ProviderError as exc:
        logger.exception("image_generation_provider_error")
        err = str(exc).lower()
        if "429" in err or "throttled" in err:
            error_text = "⏱ Provider is rate-limited. Please wait ~15 seconds and try again."
        elif "pricing guard" in err or "cost" in err:
            error_text = "💰 Blocked by cost guard (max $0.015/image). Contact support."
        elif "402" in err or "payment method" in err:
            error_text = "💳 Provider billing not configured. Contact support."
        elif "timed out" in err or "timeout" in err:
            error_text = "⏰ Generation timed out. Please try again."
        else:
            error_text = "❌ Image generation temporarily unavailable. Try again in a minute."
        try:
            await progress_msg.edit_text(error_text)
        except Exception:
            await message.answer(error_text)
    except Exception:
        logger.exception("image_generation_unexpected_error")
        try:
            await progress_msg.edit_text("❌ Unexpected error. Please try again later.")
        except Exception:
            await message.answer("❌ Unexpected error. Please try again later.")
    finally:
        await state.clear()


@router.message(GenerationStates.waiting_for_image_prompt)
async def invalid_prompt_type(message: Message) -> None:
    await message.answer("⚠️ Please send <b>text only</b> as your prompt.")
