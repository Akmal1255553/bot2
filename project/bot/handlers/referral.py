from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.helpers import build_services
from config import get_settings

router = Router()


@router.message(Command("referral"))
async def cmd_referral(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    settings = get_settings()
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)

    referral_count = await services.user_repo.count_referrals(user.telegram_id)

    bot_info = await message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user.referral_code}"

    await message.answer(
        "🔗 <b>Referral Program</b>\n\n"
        f"Share your link and earn <b>{settings.referral_bonus_images}</b> free images "
        "for every friend who joins!\n\n"
        f"📎 Your link:\n<code>{referral_link}</code>\n\n"
        f"👥 Friends referred: <b>{referral_count}</b>\n"
        f"🎁 Bonus images earned: <b>{user.referral_bonus_earned}</b>"
    )
