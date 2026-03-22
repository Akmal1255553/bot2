from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.models import Plan

from bot.handlers.helpers import build_services
from bot.i18n import normalize_language, plan_label, t
from bot.keyboards.common import (
    admin_payment_approval_keyboard,
    payment_confirmation_keyboard,
    subscription_offer_keyboard,
)
from bot.services.exceptions import AccessDeniedError

router = Router()
logger = logging.getLogger(__name__)


def _localized_error(language: str, exc: AccessDeniedError) -> str:
    code = getattr(exc, "code", "error.access_denied")
    context = getattr(exc, "context", {})
    return t(language, code, **context)


@router.message(Command("buy"))
async def cmd_buy(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    language = normalize_language(user.language or message.from_user.language_code)
    await message.answer(
        t(language, "payment.choose_plan"),
        reply_markup=subscription_offer_keyboard(
            language=language,
            basic_price=services.payment_service.price_text(Plan.BASIC),
            pro_price=services.payment_service.price_text(Plan.PRO),
        ),
    )


@router.callback_query(F.data.startswith("buy_plan:"))
async def callback_buy(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message or not query.data:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    language = normalize_language(user.language or query.from_user.language_code)

    try:
        plan_name = query.data.split("buy_plan:", maxsplit=1)[1]
        plan = services.payment_service.parse_plan(plan_name)
        offer = services.payment_service.offer(plan)
        wallet = services.payment_service.wallet_address
    except AccessDeniedError as exc:
        await query.answer(_localized_error(language, exc), show_alert=True)
        return

    instructions = t(
        language,
        "payment.instructions",
        plan=plan_label(language, offer.plan.value),
        limit=offer.monthly_limit,
        amount=offer.amount_usdt,
        wallet=wallet,
    )
    await query.message.answer(
        instructions,
        reply_markup=payment_confirmation_keyboard(language=language, plan=plan),
    )
    await query.answer()


@router.callback_query(F.data.startswith("payment:paid:"))
async def callback_i_paid(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message or not query.data:
        return

    settings = get_settings()
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)
    user_language = normalize_language(user.language or query.from_user.language_code)

    try:
        plan_name = query.data.split("payment:paid:", maxsplit=1)[1]
        plan = services.payment_service.parse_plan(plan_name)
        offer = services.payment_service.offer(plan)
    except AccessDeniedError as exc:
        await query.answer(_localized_error(user_language, exc), show_alert=True)
        return

    admin_ids = sorted(settings.admin_ids)
    if not admin_ids:
        await query.message.answer(t(user_language, "payment.no_admins"))
        await query.answer()
        return

    username = query.from_user.username or "unknown"
    for admin_id in admin_ids:
        try:
            admin_user = await services.user_repo.get_by_telegram_id(admin_id)
            admin_language = normalize_language(admin_user.language if admin_user else "en")
            await query.message.bot.send_message(
                admin_id,
                t(
                    admin_language,
                    "payment.admin_request",
                    user_id=user.telegram_id,
                    username=username,
                    plan=plan_label(admin_language, plan.value),
                    amount=offer.amount_usdt,
                ),
                reply_markup=admin_payment_approval_keyboard(
                    user_id=user.telegram_id,
                    plan=plan,
                    language=admin_language,
                ),
            )
        except Exception:
            logger.exception(
                "payment_admin_notification_failed",
                extra={
                    "admin_id": admin_id,
                    "request_user_id": user.telegram_id,
                    "plan": plan.value,
                },
            )

    await query.message.answer(t(user_language, "payment.request_sent"))
    await query.answer()


@router.callback_query(F.data.startswith("payment:approve:"))
async def callback_admin_approve(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.data or not query.message:
        return

    settings = get_settings()
    if query.from_user.id not in settings.admin_ids:
        guessed_language = normalize_language(query.from_user.language_code)
        await query.answer(t(guessed_language, "error.admin_only"), show_alert=True)
        return

    services = build_services(session)
    admin_user = await services.user_service.get_or_create(query.from_user.id)
    admin_language = normalize_language(admin_user.language)

    parts = query.data.split(":")
    if len(parts) != 4:
        await query.answer(t(admin_language, "error.invalid_payment_payload"), show_alert=True)
        return

    _, _, plan_raw, user_id_raw = parts
    try:
        plan = services.payment_service.parse_plan(plan_raw)
        target_user_id = int(user_id_raw)
    except (AccessDeniedError, ValueError):
        await query.answer(t(admin_language, "error.invalid_payment_payload"), show_alert=True)
        return

    target_user = await services.user_repo.get_by_telegram_id(target_user_id)
    if not target_user:
        await query.answer(t(admin_language, "admin.user_not_found"), show_alert=True)
        return

    updated_user = await services.payment_service.apply_successful_payment(target_user, plan)

    confirmation_text = t(
        admin_language,
        "payment.admin_approved",
        plan=plan_label(admin_language, plan.value),
        user_id=target_user_id,
    )
    if query.message:
        try:
            await query.message.edit_text(confirmation_text)
        except Exception:
            pass
    await query.answer(
        t(
            admin_language,
            "payment.admin_approved",
            plan=plan_label(admin_language, plan.value),
            user_id=target_user_id,
        )
    )

    user_language = normalize_language(updated_user.language)
    try:
        await query.message.bot.send_message(
            target_user_id,
            t(
                user_language,
                "payment.user_approved",
                plan=plan_label(user_language, plan.value),
            ),
        )
    except Exception:
        logger.exception(
            "payment_user_notification_failed",
            extra={"target_user_id": target_user_id, "plan": plan.value},
        )
