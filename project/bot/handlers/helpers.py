from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from bot.repositories.history_repository import HistoryRepository
from bot.repositories.user_repository import UserRepository
from bot.services.admin_service import AdminService
from bot.services.payment_service import PaymentService
from bot.services.subscription_service import SubscriptionService
from bot.services.user_service import UserService


@dataclass(slots=True)
class ServiceBundle:
    user_repo: UserRepository
    history_repo: HistoryRepository
    subscription_service: SubscriptionService
    user_service: UserService
    payment_service: PaymentService
    admin_service: AdminService


def build_services(session: AsyncSession) -> ServiceBundle:
    user_repo = UserRepository(session)
    history_repo = HistoryRepository(session)
    subscription_service = SubscriptionService(user_repo)
    user_service = UserService(user_repo, subscription_service)
    payment_service = PaymentService(subscription_service)
    admin_service = AdminService(user_repo, history_repo)
    return ServiceBundle(
        user_repo=user_repo,
        history_repo=history_repo,
        subscription_service=subscription_service,
        user_service=user_service,
        payment_service=payment_service,
        admin_service=admin_service,
    )
