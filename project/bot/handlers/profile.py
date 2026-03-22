from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language
from bot.utils.formatters import format_profile

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(user.language or message.from_user.language_code)
    await message.answer(format_profile(user, language))
