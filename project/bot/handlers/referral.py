from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, t
from config import get_settings

router = Router()


@router.message(Command("referral"))
async def cmd_referral(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return

    settings = get_settings()
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(user.language or message.from_user.language_code)

    referral_count = await services.user_repo.count_referrals(user.telegram_id)
    bot_info = await message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user.referral_code}"

    await message.answer(
        t(
            language,
            "referral.text",
            bonus=settings.referral_bonus_images,
            link=referral_link,
            count=referral_count,
            earned=user.referral_bonus_earned,
        )
    )
