from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.models import Language, Plan

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, t
from bot.keyboards.common import (
    language_selection_keyboard,
    start_menu_keyboard,
    subscription_offer_keyboard,
)
from bot.keyboards.generation import style_picker_keyboard
from bot.states import GenerationStates
from bot.utils.formatters import format_profile, remaining_images

router = Router()
logger = logging.getLogger(__name__)


def _build_start_text(language: str, plan: str, remaining: int) -> str:
    return (
        f"{t(language, 'app.start_title')}\n\n"
        f"{t(language, 'app.start_intro')}\n\n"
        f"{t(language, 'app.start_plan', plan=plan)}\n"
        f"{t(language, 'app.start_remaining', remaining=remaining)}\n\n"
        f"{t(language, 'app.start_menu_prompt')}"
    )


def _is_supported_language(code: str) -> bool:
    return code in {member.value for member in Language}


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    settings = get_settings()
    services = build_services(session)

    raw_args = message.text or ""
    referral_code: str | None = None
    if " " in raw_args:
        payload = raw_args.split(" ", maxsplit=1)[1].strip()
        if payload.startswith("ref_"):
            referral_code = payload[4:]

    user = await services.user_service.get_or_create(telegram_id=message.from_user.id)

    if referral_code and user.referred_by is None:
        referrer = await services.user_repo.get_by_referral_code(referral_code)
        if referrer and referrer.telegram_id != user.telegram_id:
            await services.user_repo.set_referred_by(user, referrer.telegram_id)
            await services.user_repo.apply_referral_bonus(referrer, settings.referral_bonus_images)
            logger.info(
                "referral_applied",
                extra={
                    "referrer_id": referrer.telegram_id,
                    "new_user_id": user.telegram_id,
                    "bonus": settings.referral_bonus_images,
                },
            )

    if not user.language:
        guessed_language = normalize_language(message.from_user.language_code)
        await message.answer(
            t(guessed_language, "app.language_prompt"),
            reply_markup=language_selection_keyboard(),
        )
        return

    language = normalize_language(user.language or message.from_user.language_code)
    text = _build_start_text(
        language=language,
        plan=t(language, f"app.plan_{user.plan.value.lower()}"),
        remaining=remaining_images(user),
    )
    await message.answer(text, reply_markup=start_menu_keyboard(language))


@router.callback_query(F.data.startswith("lang:set:"))
async def callback_set_language(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.data or not query.message:
        return
    selected_language = query.data.split("lang:set:", maxsplit=1)[1].strip().lower()
    if not _is_supported_language(selected_language):
        guessed_language = normalize_language(query.from_user.language_code)
        await query.answer(t(guessed_language, "error.language_not_supported"), show_alert=True)
        return

    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    await services.user_repo.set_language(user, selected_language)
    user.language = selected_language

    await query.answer(t(selected_language, "app.language_updated"))
    text = _build_start_text(
        language=selected_language,
        plan=t(selected_language, f"app.plan_{user.plan.value.lower()}"),
        remaining=remaining_images(user),
    )
    await query.message.answer(text, reply_markup=start_menu_keyboard(selected_language))


@router.callback_query(F.data == "menu:create_image")
async def callback_create_image(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    if not user.language:
        guessed_language = normalize_language(query.from_user.language_code)
        await query.message.answer(
            t(guessed_language, "app.language_prompt"),
            reply_markup=language_selection_keyboard(),
        )
        await query.answer()
        return

    language = normalize_language(user.language or query.from_user.language_code)
    await state.set_state(GenerationStates.choosing_style)
    await query.message.answer(
        t(language, "generation.choose_style"),
        reply_markup=style_picker_keyboard(language),
    )
    await query.answer()


@router.callback_query(F.data == "menu:profile")
async def callback_profile(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)
    await query.message.answer(format_profile(user, language))
    await query.answer()


@router.callback_query(F.data == "menu:buy_plan")
async def callback_buy_plan(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)
    await query.message.answer(
        t(language, "payment.choose_plan"),
        reply_markup=subscription_offer_keyboard(
            language=language,
            basic_price=services.payment_service.price_text(Plan.BASIC),
            pro_price=services.payment_service.price_text(Plan.PRO),
        ),
    )
    await query.answer()


@router.callback_query(F.data == "menu:language")
async def callback_menu_language(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.message or not query.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)
    await query.message.answer(
        t(language, "app.language_prompt"),
        reply_markup=language_selection_keyboard(),
    )
    await query.answer()


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        await message.answer(t("en", "help.text"))
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(user.language or message.from_user.language_code)
    await message.answer(t(language, "help.text"))
