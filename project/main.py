import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, ParseMode

from bot.handlers import get_main_router
from bot.middlewares.db_session import DbSessionMiddleware
from bot.middlewares.request_logging import RequestLoggingMiddleware
from bot.services.ai.factory import get_image_provider
from bot.services.generation_guard import GenerationGuard
from bot.services.generation_service import GenerationService
from bot.utils.logging_config import setup_logging
from config import get_settings
from database.session import close_db, init_db


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Main menu"),
            BotCommand(command="generate_image", description="Generate AI image"),
            BotCommand(command="profile", description="View profile and quota"),
            BotCommand(command="history", description="Generation history"),
            BotCommand(command="buy", description="Buy BASIC or PRO"),
            BotCommand(command="referral", description="Referral program"),
            BotCommand(command="help", description="Show help"),
            BotCommand(command="admin", description="Admin controls"),
        ]
    )


async def run() -> None:
    settings = get_settings()
    setup_logging()
    logger = logging.getLogger(__name__)

    bot: Bot | None = None
    await init_db()
    logger.info("database_ready")

    try:
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        dp = Dispatcher()
        dp.include_router(get_main_router())

        dp.message.middleware(RequestLoggingMiddleware())
        dp.callback_query.middleware(RequestLoggingMiddleware())
        dp.message.middleware(DbSessionMiddleware())
        dp.callback_query.middleware(DbSessionMiddleware())

        generation_service = GenerationService(image_provider=get_image_provider())
        generation_guard = GenerationGuard()

        await set_bot_commands(bot)
        logger.info("bot_starting")

        await dp.start_polling(
            bot,
            settings=settings,
            generation_service=generation_service,
            generation_guard=generation_guard,
            allowed_updates=dp.resolve_used_update_types(),
        )
    except asyncio.CancelledError:
        logger.info("bot_polling_cancelled")
        raise
    finally:
        if bot is not None:
            with contextlib.suppress(Exception):
                await bot.session.close()
        with contextlib.suppress(Exception):
            await close_db()
        logger.info("shutdown_complete")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("bot_stopped")
