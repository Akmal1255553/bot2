from __future__ import annotations

import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, plan_label, t
from bot.services.exceptions import AccessDeniedError
from bot.utils.formatters import format_profile

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("admin"))
async def cmd_admin(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    settings: Settings,
) -> None:
    if not message.from_user:
        return

    guessed_language = normalize_language(message.from_user.language_code)
    if message.from_user.id not in settings.admin_ids:
        await message.answer(t(guessed_language, "admin.access_denied"))
        return

    services = build_services(session)
    admin_user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(admin_user.language)
    args = (command.args or "").strip()

    if not args:
        stats = await services.admin_service.get_stats()
        await message.answer(
            t(
                language,
                "admin.panel",
                total_users=stats.total_users,
                paid_users=stats.paid_users,
                today_generations=stats.today_generations,
            )
        )
        return

    parts = args.split(maxsplit=1)
    sub_command = parts[0].lower()
    sub_args = parts[1] if len(parts) > 1 else ""

    if sub_command == "stats":
        stats = await services.admin_service.get_stats()
        await message.answer(
            t(
                language,
                "admin.stats",
                total_users=stats.total_users,
                paid_users=stats.paid_users,
                today_generations=stats.today_generations,
            )
        )
        return

    if sub_command == "user":
        if not sub_args.strip():
            await message.answer(t(language, "admin.usage_user"))
            return
        try:
            target_id = int(sub_args.strip())
        except ValueError:
            await message.answer(t(language, "admin.invalid_telegram_id"))
            return

        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer(t(language, "admin.user_not_found"))
            return

        referral_count = await services.user_repo.count_referrals(target_user.telegram_id)
        target_language = normalize_language(target_user.language)
        await message.answer(
            t(
                language,
                "admin.user_details",
                user_id=target_id,
                profile=format_profile(target_user, target_language),
                referrals=referral_count,
                bonus=target_user.referral_bonus_earned,
            )
        )
        return

    if sub_command == "grant":
        grant_parts = sub_args.strip().split()
        if len(grant_parts) != 2:
            await message.answer(t(language, "admin.usage_grant"))
            return
        try:
            target_id = int(grant_parts[0])
            count = int(grant_parts[1])
        except ValueError:
            await message.answer(t(language, "admin.invalid_arguments"))
            return
        if count <= 0 or count > 1000:
            await message.answer(t(language, "admin.invalid_count"))
            return

        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer(t(language, "admin.user_not_found"))
            return

        await services.user_repo.grant_bonus(target_user, count)
        await message.answer(
            t(language, "admin.granted", count=count, user_id=target_id)
        )
        return

    if sub_command == "plan":
        plan_parts = sub_args.strip().split()
        if len(plan_parts) != 2:
            await message.answer(t(language, "admin.usage_plan"))
            return
        try:
            target_id = int(plan_parts[0])
            plan = services.payment_service.parse_plan(plan_parts[1])
        except ValueError:
            await message.answer(t(language, "admin.invalid_telegram_id"))
            return
        except AccessDeniedError as exc:
            await message.answer(t(language, exc.code, **exc.context))
            return

        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer(t(language, "admin.user_not_found"))
            return

        await services.subscription_service.activate_plan(target_user, plan)
        await message.answer(
            t(
                language,
                "admin.plan_activated",
                plan=plan_label(language, plan.value),
                user_id=target_id,
            )
        )
        return

    if sub_command == "broadcast":
        if not sub_args.strip():
            await message.answer(t(language, "admin.usage_broadcast"))
            return

        broadcast_text = sub_args.strip()
        user_ids = await services.admin_service.get_all_user_ids()
        sent = 0
        failed = 0
        progress = await message.answer(
            t(language, "admin.broadcast_start", count=len(user_ids))
        )

        for uid in user_ids:
            try:
                await message.bot.send_message(uid, broadcast_text)
                sent += 1
            except Exception:
                failed += 1
            if sent % 25 == 0:
                await asyncio.sleep(1)

        try:
            await progress.edit_text(
                t(language, "admin.broadcast_done", sent=sent, failed=failed)
            )
        except Exception:
            pass
        return

    await message.answer(t(language, "admin.unknown_command"))
