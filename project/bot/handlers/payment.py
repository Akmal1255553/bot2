from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings

from bot.handlers.helpers import build_services
from bot.keyboards.common import subscription_offer_keyboard
from bot.services.exceptions import AccessDeniedError

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("buy"))
async def cmd_buy(message: Message) -> None:
    await message.answer("Choose a plan:", reply_markup=subscription_offer_keyboard())


@router.callback_query(F.data.startswith("buy_plan:"))
async def callback_buy(query: CallbackQuery, session: AsyncSession) -> None:
    if not query.from_user or not query.message or not query.data:
        return
    services = build_services(session)
    user = await services.user_service.get_or_create(query.from_user.id)

    try:
        plan_name = query.data.split("buy_plan:", maxsplit=1)[1]
        plan = services.payment_service.parse_plan(plan_name)
        invoice = services.payment_service.build_invoice(user.telegram_id, plan)
    except AccessDeniedError as exc:
        await query.answer(str(exc), show_alert=True)
        return

    try:
        await query.message.answer_invoice(
            title=invoice.title,
            description=invoice.description,
            payload=invoice.payload,
            provider_token=services.payment_service.provider_token,
            currency=invoice.currency,
            prices=invoice.prices,
            start_parameter=f"plan_{plan.value.lower()}",
        )
        await query.answer()
    except TelegramBadRequest as exc:
        logger.error(
            "invoice_send_failed",
            extra={
                "telegram_user_id": user.telegram_id,
                "plan": plan.value,
                "telegram_api_response": getattr(exc, "message", str(exc)),
            },
        )
        await query.answer("Payments are temporarily unavailable.", show_alert=True)


@router.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery, session: AsyncSession, settings: Settings
) -> None:
    services = build_services(session)
    try:
        plan, user_id = services.payment_service.parse_payload(pre_checkout_query.invoice_payload)
        if user_id != pre_checkout_query.from_user.id:
            raise AccessDeniedError("Invoice user mismatch.")
        if pre_checkout_query.total_amount != services.payment_service.expected_price(plan):
            raise AccessDeniedError("Invoice amount mismatch.")
        if pre_checkout_query.currency != settings.currency.upper():
            raise AccessDeniedError("Invoice currency mismatch.")
    except AccessDeniedError:
        try:
            await pre_checkout_query.answer(ok=False, error_message="Invalid invoice payload.")
        except TelegramBadRequest as exc:
            logger.error(
                "pre_checkout_reject_failed",
                extra={
                    "telegram_user_id": pre_checkout_query.from_user.id,
                    "telegram_api_response": getattr(exc, "message", str(exc)),
                },
            )
        return
    try:
        await pre_checkout_query.answer(ok=True)
    except TelegramBadRequest as exc:
        logger.error(
            "pre_checkout_accept_failed",
            extra={
                "telegram_user_id": pre_checkout_query.from_user.id,
                "telegram_api_response": getattr(exc, "message", str(exc)),
            },
        )


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, session: AsyncSession) -> None:
    if not message.from_user or not message.successful_payment:
        return

    services = build_services(session)
    user = await services.user_service.get_or_create(message.from_user.id)
    payment = message.successful_payment

    try:
        plan, payload_user_id = services.payment_service.parse_payload(payment.invoice_payload)
        if payload_user_id != user.telegram_id:
            raise AccessDeniedError("Invoice user mismatch.")
        if payment.total_amount != services.payment_service.expected_price(plan):
            raise AccessDeniedError("Invoice amount mismatch.")
        if payment.currency != services.payment_service.settings.currency.upper():
            raise AccessDeniedError("Invoice currency mismatch.")
        updated_user = await services.payment_service.apply_successful_payment(user=user, plan=plan)
        logger.info(
            "payment_processed",
            extra={
                "telegram_user_id": user.telegram_id,
                "plan": plan.value,
                "currency": payment.currency,
                "amount": payment.total_amount,
                "telegram_payment_charge_id": payment.telegram_payment_charge_id,
                "provider_payment_charge_id": payment.provider_payment_charge_id,
            },
        )
        await message.answer(
            f"Payment successful. Plan activated: {updated_user.plan.value}\n"
            f"Expiry: {updated_user.subscription_expiry:%Y-%m-%d %H:%M UTC}"
        )
    except AccessDeniedError as exc:
        logger.warning(
            "payment_validation_failed",
            extra={
                "error": str(exc),
                "telegram_user_id": user.telegram_id,
                "currency": payment.currency,
                "amount": payment.total_amount,
            },
        )
        await message.answer("Payment received but validation failed. Contact support.")
    except Exception:
        logger.exception(
            "payment_processing_error",
            extra={"telegram_user_id": user.telegram_id, "payload": payment.invoice_payload},
        )
        await message.answer("Payment received, but activation failed temporarily. Contact support.")
