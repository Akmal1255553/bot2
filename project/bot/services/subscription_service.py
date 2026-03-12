from __future__ import annotations

from datetime import datetime, timezone

from config import get_settings
from database.models import Plan, User

from bot.repositories.user_repository import UserRepository
from bot.services.exceptions import AccessDeniedError


class SubscriptionService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        self.settings = get_settings()

    async def sync_status(self, user: User) -> User:
        now = datetime.now(timezone.utc)
        if user.plan in {Plan.BASIC, Plan.PRO} and (
            user.subscription_expiry is None or user.subscription_expiry <= now
        ):
            await self.user_repo.downgrade_to_free(user)
            user.plan = Plan.FREE
            user.subscription_expiry = None
            user.images_used_this_month = 0
        return user

    def monthly_limit(self, plan: Plan) -> int:
        if plan == Plan.BASIC:
            return self.settings.basic_monthly_images
        if plan == Plan.PRO:
            return self.settings.pro_monthly_images
        return 0

    async def ensure_can_generate_image(self, user: User) -> None:
        await self.sync_status(user)
        if user.plan == Plan.FREE:
            if user.free_images_left > 0:
                return
            raise AccessDeniedError("Free image limit reached. Upgrade with /buy.")

        limit = self.monthly_limit(user.plan)
        if user.images_used_this_month >= limit:
            raise AccessDeniedError(f"Monthly image limit reached for {user.plan.value} plan.")

    async def consume_image_generation(self, user: User) -> None:
        if user.plan == Plan.FREE:
            await self.user_repo.consume_free_image(user)
            return
        await self.user_repo.consume_paid_image(user)

    async def activate_plan(self, user: User, plan: Plan) -> User:
        return await self.user_repo.activate_plan(user, plan=plan, days=self.settings.subscription_days)
