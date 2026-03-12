from __future__ import annotations

from database.models import User

from bot.repositories.user_repository import UserRepository
from bot.services.subscription_service import SubscriptionService


class UserService:
    def __init__(self, user_repo: UserRepository, subscription_service: SubscriptionService) -> None:
        self.user_repo = user_repo
        self.subscription_service = subscription_service

    async def get_or_create(self, telegram_id: int) -> User:
        user = await self.user_repo.get_or_create(telegram_id)
        return await self.subscription_service.sync_status(user)
