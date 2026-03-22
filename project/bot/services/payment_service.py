from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from config import get_settings
from database.models import Plan, User

from bot.services.exceptions import AccessDeniedError
from bot.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PlanOffer:
    plan: Plan
    monthly_limit: int
    amount_usdt: str


class PaymentService:
    def __init__(self, subscription_service: SubscriptionService) -> None:
        self.subscription_service = subscription_service
        self.settings = get_settings()
        self._monthly_limit_by_plan = {
            Plan.BASIC: self.settings.basic_monthly_images,
            Plan.PRO: self.settings.pro_monthly_images,
        }

    def parse_plan(self, value: str) -> Plan:
        plan = value.upper().strip()
        if plan == Plan.BASIC.value:
            return Plan.BASIC
        if plan == Plan.PRO.value:
            return Plan.PRO
        raise AccessDeniedError("error.unsupported_plan")

    def _price_value(self, plan: Plan) -> Decimal:
        try:
            if plan == Plan.BASIC:
                return Decimal(str(self.settings.basic_plan_price_usdt))
            if plan == Plan.PRO:
                return Decimal(str(self.settings.pro_plan_price_usdt))
        except InvalidOperation as exc:
            raise AccessDeniedError("error.unsupported_plan") from exc
        raise AccessDeniedError("error.unsupported_plan")

    def price_text(self, plan: Plan) -> str:
        price = self._price_value(plan)
        return f"{price.quantize(Decimal('0.01'))}"

    def offer(self, plan: Plan) -> PlanOffer:
        limit = self._monthly_limit_by_plan.get(plan)
        if limit is None:
            raise AccessDeniedError("error.unsupported_plan")
        return PlanOffer(
            plan=plan,
            monthly_limit=limit,
            amount_usdt=self.price_text(plan),
        )

    @property
    def wallet_address(self) -> str:
        wallet = self.settings.usdt_trc20_wallet.strip()
        if not wallet:
            raise AccessDeniedError("payment.wallet_missing")
        return wallet

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
