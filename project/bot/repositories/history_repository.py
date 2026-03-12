from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import GenerationHistory


class HistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_generation(
        self,
        user_id: int,
        prompt: str,
        style: str,
        aspect_ratio: str,
        image_url: str | None,
        plan: str,
    ) -> GenerationHistory:
        entry = GenerationHistory(
            user_id=user_id,
            prompt=prompt,
            style=style,
            aspect_ratio=aspect_ratio,
            image_url=image_url,
            plan_at_generation=plan,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_recent(
        self, user_id: int, limit: int = 5, offset: int = 0
    ) -> list[GenerationHistory]:
        stmt: Select[tuple[GenerationHistory]] = (
            select(GenerationHistory)
            .where(GenerationHistory.user_id == user_id)
            .order_by(GenerationHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_user_total(self, user_id: int) -> int:
        stmt = select(func.count(GenerationHistory.id)).where(
            GenerationHistory.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def count_today_all(self) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        stmt = select(func.count(GenerationHistory.id)).where(
            GenerationHistory.created_at >= today_start
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)
