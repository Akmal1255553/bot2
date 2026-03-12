from __future__ import annotations

import logging
from dataclasses import dataclass

from aiogram.types import LabeledPrice

from config import get_settings
from database.models import Plan, User

from bot.services.exceptions import AccessDeniedError
from bot.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class InvoiceData:
    title: str
    description: str
    payload: str
    prices: list[LabeledPrice]
    currency: str
    plan: Plan


class PaymentService:
    def __init__(self, subscription_service: SubscriptionService) -> None:
        self.subscription_service = subscription_service
        self.settings = get_settings()
        self._price_by_plan = {
            Plan.BASIC: self.settings.basic_plan_price_cents,
            Plan.PRO: self.settings.pro_plan_price_cents,
        }

    def _validate_runtime_payment_config(self) -> None:
        token = self.settings.provider_token.strip()
        if not token:
            raise AccessDeniedError("Payments are not configured: PROVIDER_TOKEN is empty.")
        if self.settings.currency != self.settings.currency.upper():
            raise AccessDeniedError("Payments are misconfigured: CURRENCY must be uppercase.")
        for name, value in (
            ("BASIC_PLAN_PRICE_CENTS", self.settings.basic_plan_price_cents),
            ("PRO_PLAN_PRICE_CENTS", self.settings.pro_plan_price_cents),
        ):
            if not isinstance(value, int):
                raise AccessDeniedError(f"Payments are misconfigured: {name} must be an integer.")
            if value <= 0:
                raise AccessDeniedError(f"Payments are misconfigured: {name} must be greater than 0.")

    def parse_plan(self, value: str) -> Plan:
        plan = value.upper().strip()
        if plan == Plan.BASIC.value:
            return Plan.BASIC
        if plan == Plan.PRO.value:
            return Plan.PRO
        raise AccessDeniedError("Unsupported plan.")

    def expected_price(self, plan: Plan) -> int:
        price = self._price_by_plan.get(plan)
        if price is None:
            raise AccessDeniedError("Unsupported plan.")
        if not isinstance(price, int):
            raise AccessDeniedError("Plan price must be integer cents.")
        return price

    def build_invoice(self, user_id: int, plan: Plan) -> InvoiceData:
        self._validate_runtime_payment_config()
        amount = self.expected_price(plan)
        label = f"{plan.value} monthly"
        payload = f"plan:{plan.value}:user:{user_id}"
        return InvoiceData(
            title=f"AI Image Bot {plan.value}",
            description="Monthly AI image plan",
            payload=payload,
            prices=[LabeledPrice(label=label, amount=amount)],
            currency=self.settings.currency.upper(),
            plan=plan,
        )

    def parse_payload(self, payload: str) -> tuple[Plan, int]:
        parts = payload.split(":")
        if len(parts) != 4 or parts[0] != "plan" or parts[2] != "user":
            raise AccessDeniedError("Invalid payment payload.")
        plan = self.parse_plan(parts[1])
        try:
            user_id = int(parts[3])
        except ValueError as exc:
            raise AccessDeniedError("Invalid payment payload.") from exc
        return plan, user_id

    @property
    def provider_token(self) -> str:
        self._validate_runtime_payment_config()
        return self.settings.provider_token.strip()

    async def apply_successful_payment(self, user: User, plan: Plan) -> User:
        logger.info(
            "activating_subscription",
            extra={
                "telegram_user_id": user.telegram_id,
                "plan": plan.value,
                "subscription_days": self.settings.subscription_days,
            },
        )
        return await self.subscription_service.activate_plan(user, plan)
