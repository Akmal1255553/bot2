from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.models import Plan, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings = get_settings()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt: Select[tuple[User]] = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int) -> User:
        user = User(
            telegram_id=telegram_id,
            plan=Plan.FREE,
            free_images_left=self.settings.free_images_default,
            images_used_this_month=0,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, telegram_id: int) -> User:
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            return existing
        return await self.create(telegram_id)

    async def consume_free_image(self, user: User) -> None:
        if user.free_images_left <= 0:
            return
        user.free_images_left -= 1
        await self.session.commit()

    async def consume_paid_image(self, user: User) -> None:
        user.images_used_this_month += 1
        await self.session.commit()

    async def activate_plan(self, user: User, plan: Plan, days: int) -> User:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        user.plan = plan
        user.subscription_expiry = now + timedelta(days=days)
        user.images_used_this_month = 0
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def downgrade_to_free(self, user: User) -> None:
        user.plan = Plan.FREE
        user.subscription_expiry = None
        user.images_used_this_month = 0
        await self.session.commit()

    async def stats_total_users(self) -> int:
        stmt = select(func.count(User.id))
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    # --- Referral methods ---

    async def get_by_referral_code(self, code: str) -> User | None:
        stmt: Select[tuple[User]] = select(User).where(User.referral_code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def apply_referral_bonus(self, referrer: User, bonus_images: int) -> None:
        referrer.free_images_left += bonus_images
        referrer.referral_bonus_earned += bonus_images
        await self.session.commit()

    async def count_referrals(self, telegram_id: int) -> int:
        stmt = select(func.count(User.id)).where(User.referred_by == telegram_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def set_referred_by(self, user: User, referrer_telegram_id: int) -> None:
        user.referred_by = referrer_telegram_id
        await self.session.commit()

    # --- Admin methods ---

    async def stats_paid_users(self) -> int:
        stmt = select(func.count(User.id)).where(User.plan.in_([Plan.BASIC, Plan.PRO]))
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def get_all_telegram_ids(self) -> list[int]:
        stmt = select(User.telegram_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def grant_bonus(self, user: User, count: int) -> None:
        user.free_images_left += count
        await self.session.commit()
