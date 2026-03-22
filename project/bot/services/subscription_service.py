from __future__ import annotations

from datetime import datetime, timedelta, timezone

from config import get_settings
from database.models import Plan, User

from bot.repositories.user_repository import UserRepository
from bot.services.exceptions import AccessDeniedError


class SubscriptionService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        self.settings = get_settings()

    @staticmethod
    def _as_utc(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    async def sync_status(self, user: User) -> User:
        now = datetime.now(timezone.utc)
        expiry = self._as_utc(user.subscription_expiry)

        if user.plan in {Plan.BASIC, Plan.PRO} and (
            expiry is None or expiry <= now
        ):
            await self.user_repo.downgrade_to_free(user)
            user.plan = Plan.FREE
            user.subscription_expiry = None
            user.images_used_this_month = 0
            user.usage_period_started_at = now
            return user

        if user.plan in {Plan.BASIC, Plan.PRO}:
            cycle_start = self._as_utc(user.usage_period_started_at)
            cycle_duration = timedelta(days=self.settings.subscription_days)
            if cycle_start is None or now >= cycle_start + cycle_duration:
                await self.user_repo.reset_paid_usage_cycle(user, now)
                user.images_used_this_month = 0
                user.usage_period_started_at = now

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
            raise AccessDeniedError("error.free_limit_reached")

        limit = self.monthly_limit(user.plan)
        if user.images_used_this_month >= limit:
            raise AccessDeniedError(
                "error.monthly_limit_reached",
                plan=user.plan.value,
            )

    async def consume_image_generation(self, user: User) -> None:
        if user.plan == Plan.FREE:
            await self.user_repo.consume_free_image(user)
            return
        await self.user_repo.consume_paid_image(user)

    async def ensure_request_limit(self, user: User) -> None:
        now = datetime.now(timezone.utc)
        if user.plan == Plan.FREE:
            limit = self.settings.free_request_window_limit
        else:
            limit = self.settings.paid_request_window_limit

        is_allowed = await self.user_repo.reserve_request_slot(
            user=user,
            now=now,
            window_seconds=self.settings.request_window_seconds,
            limit=limit,
        )
        if not is_allowed:
            raise AccessDeniedError(
                "error.request_rate_limited",
                seconds=self.settings.request_window_seconds,
            )

    async def activate_plan(self, user: User, plan: Plan) -> User:
        return await self.user_repo.activate_plan(user, plan=plan, days=self.settings.subscription_days)
