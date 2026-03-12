from aiogram import Router

from bot.handlers.admin import router as admin_router
from bot.handlers.generation import router as generation_router
from bot.handlers.history import router as history_router
from bot.handlers.payment import router as payment_router
from bot.handlers.profile import router as profile_router
from bot.handlers.referral import router as referral_router
from bot.handlers.start import router as start_router


def get_main_router() -> Router:
    router = Router()
    router.include_router(start_router)
    router.include_router(profile_router)
    router.include_router(generation_router)
    router.include_router(history_router)
    router.include_router(referral_router)
    router.include_router(payment_router)
    router.include_router(admin_router)
    return router
