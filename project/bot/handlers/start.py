from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings

from bot.handlers.helpers import build_services
from bot.keyboards.common import start_menu_keyboard, subscription_offer_keyboard
from bot.keyboards.generation import style_picker_keyboard
from bot.states import GenerationStates
from bot.utils.formatters import format_profile, remaining_images

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    settings = get_settings()
    services = build_services(session)

    # Check if this is a referral deep link: /start ref_XXXXXXXX
    raw_args = message.text or ""
    referral_code: str | None = None
    if " " in raw_args:
        payload = raw_args.split(" ", maxsplit=1)[1].strip()
        if payload.startswith("ref_"):
            referral_code = payload[4:]

    user = await services.user_service.get_or_create(telegram_id=message.from_user.id)

    # Process referral if user is new (no referred_by yet) and valid code
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

    remaining = remaining_images(user)
    text = (
        "🤖 <b>Welcome to AI Creator Bot!</b>\n\n"
        "Generate stunning AI images in seconds.\n\n"
        "<b>📋 Plans:</b>\n"
        "  🆓 <b>FREE</b> — 3 images, 1024×1024\n"
        "  ⭐ <b>BASIC</b> — 80/month, $7\n"
        "  💎 <b>PRO</b> — 250/month, $15\n\n"
        f"Your plan: <b>{user.plan.value}</b>  •  Remaining: <b>{remaining}</b>\n\n"
        "Choose an option below ⬇️"
    )
    await message.answer(text, reply_markup=start_menu_keyboard())


@router.callback_query(F.data == "menu:create_image")
async def callback_create_image(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    services = build_services(session)
    await services.user_service.get_or_create(query.from_user.id)
    await state.set_state(GenerationStates.choosing_style)
    await query.message.answer(
        "🎨 <b>Choose an art style:</b>",
        reply_markup=style_picker_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data == "menu:profile")
async def callback_profile(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    await query.message.answer(format_profile(user))
    await query.answer()


@router.callback_query(F.data == "menu:history")
async def callback_history(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    from bot.handlers.history import _send_history_page
    await _send_history_page(query.message, session, offset=0, from_user_id=query.from_user.id)
    await query.answer()


@router.callback_query(F.data == "menu:plans")
async def callback_plans(query: CallbackQuery) -> None:
    if not query.message:
        return
    await query.message.answer(
        "💳 <b>Choose a plan:</b>",
        reply_markup=subscription_offer_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data == "menu:referral")
async def callback_referral(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message:
        return
    settings = get_settings()
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    referral_count = await services.user_repo.count_referrals(user.telegram_id)
    bot_info = await query.message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user.referral_code}"
    await query.message.answer(
        "🔗 <b>Referral Program</b>\n\n"
        f"Share your link and earn <b>{settings.referral_bonus_images}</b> free images "
        "for every friend who joins!\n\n"
        f"📎 Your link:\n<code>{referral_link}</code>\n\n"
        f"👥 Friends referred: <b>{referral_count}</b>\n"
        f"🎁 Bonus images earned: <b>{user.referral_bonus_earned}</b>"
    )
    await query.answer()


@router.callback_query(F.data == "menu:help")
async def callback_help(query: CallbackQuery) -> None:
    if not query.message:
        return
    await query.message.answer(
        "❓ <b>Help</b>\n\n"
        "🖼 <b>Create Image</b> — pick a style, aspect ratio, then enter a prompt\n"
        "📈 <b>Profile</b> — view your plan, usage, and expiry\n"
        "📜 <b>History</b> — see your recent generations\n"
        "💳 <b>Plans</b> — upgrade to BASIC or PRO\n"
        "🔗 <b>Referral</b> — invite friends, earn free images\n\n"
        "💡 <i>Rate limits apply globally and per user to keep the service stable.</i>"
    )
    await query.answer()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "❓ <b>Help</b>\n\n"
        "Use /start to open the main menu, or:\n\n"
        "/generate_image — create an AI image\n"
        "/profile — view your plan and usage\n"
        "/history — recent generations\n"
        "/buy — upgrade your plan\n"
        "/referral — invite friends, earn images\n"
        "/help — show this message"
    )
