from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import LANGUAGE_LABELS, t
from database.models import Plan


def language_selection_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=LANGUAGE_LABELS["en"], callback_data="lang:set:en"),
            InlineKeyboardButton(text=LANGUAGE_LABELS["ru"], callback_data="lang:set:ru"),
            InlineKeyboardButton(text=LANGUAGE_LABELS["uz"], callback_data="lang:set:uz"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subscription_offer_keyboard(
    language: str,
    basic_price: str,
    pro_price: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "button.buy_basic", price=basic_price),
                    callback_data="buy_plan:BASIC",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "button.buy_pro", price=pro_price),
                    callback_data="buy_plan:PRO",
                )
            ],
        ]
    )


def payment_confirmation_keyboard(language: str, plan: Plan) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "button.i_paid"),
                    callback_data=f"payment:paid:{plan.value}",
                )
            ]
        ]
    )


def admin_payment_approval_keyboard(user_id: int, plan: Plan, language: str) -> InlineKeyboardMarkup:
    key = "button.approve_basic" if plan == Plan.BASIC else "button.approve_pro"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, key),
                    callback_data=f"payment:approve:{plan.value}:{user_id}",
                )
            ]
        ]
    )


def start_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "button.generate_image"),
                    callback_data="menu:create_image",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "button.profile"),
                    callback_data="menu:profile",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "button.buy_plan"),
                    callback_data="menu:buy_plan",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "button.change_language"),
                    callback_data="menu:language",
                )
            ],
        ]
    )


def history_pagination_keyboard(
    offset: int,
    total: int,
    language: str,
    page_size: int = 5,
) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if offset > 0:
        buttons.append(
            InlineKeyboardButton(
                text=t(language, "button.prev"),
                callback_data=f"history:page:{offset - page_size}",
            )
        )
    if offset + page_size < total:
        buttons.append(
            InlineKeyboardButton(
                text=t(language, "button.next"),
                callback_data=f"history:page:{offset + page_size}",
            )
        )
    if not buttons:
        return InlineKeyboardMarkup(inline_keyboard=[])
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
