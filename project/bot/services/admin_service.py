from __future__ import annotations

from dataclasses import dataclass

from bot.repositories.history_repository import HistoryRepository
from bot.repositories.user_repository import UserRepository


@dataclass(slots=True)
class AdminStats:
    total_users: int
    paid_users: int
    today_generations: int


class AdminService:
    def __init__(self, user_repo: UserRepository, history_repo: HistoryRepository) -> None:
        self.user_repo = user_repo
        self.history_repo = history_repo

    async def get_stats(self) -> AdminStats:
        total_users = await self.user_repo.stats_total_users()
        paid_users = await self.user_repo.stats_paid_users()
        today_gens = await self.history_repo.count_today_all()
        return AdminStats(
            total_users=total_users,
            paid_users=paid_users,
            today_generations=today_gens,
        )

    async def get_all_user_ids(self) -> list[int]:
        return await self.user_repo.get_all_telegram_ids()
