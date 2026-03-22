from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, t
from bot.keyboards.common import history_pagination_keyboard
from bot.utils.formatters import format_history_entry

router = Router()

PAGE_SIZE = 5


@router.message(Command("history"))
async def cmd_history(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    await _send_history_page(message, session, offset=0)


@router.callback_query(F.data.startswith("history:page:"))
async def callback_history_page(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message or not query.data:
        return
    offset = int(query.data.split("history:page:")[1])
    if offset < 0:
        offset = 0
    await _send_history_page(
        query.message,
        session,
        offset=offset,
        from_user_id=query.from_user.id,
    )
    await query.answer()


async def _send_history_page(
    message: Message,
    session: AsyncSession,
    offset: int,
    from_user_id: int | None = None,
) -> None:
    user_id = from_user_id or (message.from_user.id if message.from_user else None)
    if not user_id:
        return

    services = build_services(session)
    user = await services.user_service.get_or_create(user_id)
    language = normalize_language(user.language)

    total = await services.history_repo.count_user_total(user.id)
    if total == 0:
        await message.answer(
            f"{t(language, 'history.title')}\n\n{t(language, 'history.empty')}"
        )
        return

    entries = await services.history_repo.get_recent(user.id, limit=PAGE_SIZE, offset=offset)
    page_text = t(
        language,
        "history.page",
        start=offset + 1,
        end=offset + len(entries),
        total=total,
    )

    lines = [f"{t(language, 'history.title')} ({page_text})\n"]
    for index, entry in enumerate(entries, start=offset + 1):
        lines.append(format_history_entry(entry, index, language))

    keyboard = history_pagination_keyboard(
        offset=offset,
        total=total,
        language=language,
        page_size=PAGE_SIZE,
    )
    await message.answer("\n\n".join(lines), reply_markup=keyboard)
