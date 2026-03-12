from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, TelegramObject

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            logger.info(
                "incoming_message",
                extra={
                    "telegram_user_id": event.from_user.id,
                    "username": event.from_user.username,
                    "chat_id": event.chat.id,
                    "text": event.text,
                },
            )
        elif isinstance(event, CallbackQuery) and event.from_user:
            logger.info(
                "incoming_callback",
                extra={
                    "telegram_user_id": event.from_user.id,
                    "username": event.from_user.username,
                    "data": event.data,
                },
            )
        elif isinstance(event, PreCheckoutQuery):
            logger.info(
                "incoming_pre_checkout",
                extra={
                    "telegram_user_id": event.from_user.id,
                    "invoice_payload": event.invoice_payload,
                },
            )
        return await handler(event, data)
