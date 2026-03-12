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
from bot.services.exceptions import AccessDeniedError
from bot.utils.formatters import format_profile, plan_badge

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
    if message.from_user.id not in settings.admin_ids:
        await message.answer("⛔ Access denied.")
        return

    services = build_services(session)
    args = (command.args or "").strip()

    if not args:
        stats = await services.admin_service.get_stats()
        await message.answer(
            "🛡️ <b>Admin Panel</b>\n\n"
            f"👥 Total users: <b>{stats.total_users}</b>\n"
            f"💳 Paid users: <b>{stats.paid_users}</b>\n"
            f"📊 Today's generations: <b>{stats.today_generations}</b>\n\n"
            "<b>Commands:</b>\n"
            "<code>/admin stats</code> — dashboard\n"
            "<code>/admin user &lt;id&gt;</code> — lookup user\n"
            "<code>/admin grant &lt;id&gt; &lt;N&gt;</code> — give bonus images\n"
            "<code>/admin plan &lt;id&gt; &lt;BASIC|PRO&gt;</code> — set plan\n"
            "<code>/admin broadcast &lt;message&gt;</code> — message all users"
        )
        return

    parts = args.split(maxsplit=1)
    sub_command = parts[0].lower()
    sub_args = parts[1] if len(parts) > 1 else ""

    if sub_command == "stats":
        stats = await services.admin_service.get_stats()
        await message.answer(
            "📊 <b>Bot Statistics</b>\n\n"
            f"👥 Total users: <b>{stats.total_users}</b>\n"
            f"💳 Paid users: <b>{stats.paid_users}</b>\n"
            f"📈 Generations today: <b>{stats.today_generations}</b>\n"
        )

    elif sub_command == "user":
        if not sub_args.strip():
            await message.answer("Usage: <code>/admin user &lt;telegram_id&gt;</code>")
            return
        try:
            target_id = int(sub_args.strip())
        except ValueError:
            await message.answer("⚠️ Invalid telegram_id.")
            return
        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ User not found.")
            return
        referral_count = await services.user_repo.count_referrals(target_user.telegram_id)
        await message.answer(
            f"👤 <b>User {target_id}</b>\n\n"
            + format_profile(target_user)
            + f"\n🔗 Referrals: <b>{referral_count}</b>\n"
            f"🎁 Referral bonus: <b>{target_user.referral_bonus_earned}</b>"
        )

    elif sub_command == "grant":
        grant_parts = sub_args.strip().split()
        if len(grant_parts) != 2:
            await message.answer("Usage: <code>/admin grant &lt;telegram_id&gt; &lt;count&gt;</code>")
            return
        try:
            target_id = int(grant_parts[0])
            count = int(grant_parts[1])
        except ValueError:
            await message.answer("⚠️ Invalid arguments.")
            return
        if count <= 0 or count > 1000:
            await message.answer("⚠️ Count must be 1–1000.")
            return
        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ User not found.")
            return
        await services.user_repo.grant_bonus(target_user, count)
        await message.answer(f"✅ Granted <b>{count}</b> bonus images to user {target_id}.")

    elif sub_command == "plan":
        plan_parts = sub_args.strip().split()
        if len(plan_parts) != 2:
            await message.answer("Usage: <code>/admin plan &lt;telegram_id&gt; &lt;BASIC|PRO&gt;</code>")
            return
        try:
            target_id = int(plan_parts[0])
            plan = services.payment_service.parse_plan(plan_parts[1])
        except ValueError:
            await message.answer("⚠️ Invalid telegram_id.")
            return
        except AccessDeniedError:
            await message.answer("⚠️ Plan must be BASIC or PRO.")
            return
        target_user = await services.user_repo.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ User not found.")
            return
        await services.subscription_service.activate_plan(target_user, plan)
        badge = plan_badge(plan)
        await message.answer(f"{badge} Plan <b>{plan.value}</b> activated for user {target_id}.")

    elif sub_command == "broadcast":
        if not sub_args.strip():
            await message.answer("Usage: <code>/admin broadcast &lt;message&gt;</code>")
            return
        broadcast_text = sub_args.strip()
        user_ids = await services.admin_service.get_all_user_ids()
        sent = 0
        failed = 0
        progress = await message.answer(
            f"📢 Broadcasting to <b>{len(user_ids)}</b> users..."
        )
        for uid in user_ids:
            try:
                await message.bot.send_message(uid, broadcast_text)
                sent += 1
            except Exception:
                failed += 1
            if sent % 25 == 0:
                await asyncio.sleep(1)  # Telegram rate limit
        try:
            await progress.edit_text(
                f"📢 <b>Broadcast complete</b>\n\n"
                f"✅ Sent: {sent}\n"
                f"❌ Failed: {failed}"
            )
        except Exception:
            pass

    else:
        await message.answer(
            "⚠️ Unknown command. Use <code>/admin</code> for available commands."
        )
