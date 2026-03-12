from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscription_offer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Buy BASIC ($7/mo)", callback_data="buy_plan:BASIC")],
            [InlineKeyboardButton(text="💎 Buy PRO ($15/mo)", callback_data="buy_plan:PRO")],
        ]
    )


def start_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Create Image", callback_data="menu:create_image")],
            [
                InlineKeyboardButton(text="📈 Profile", callback_data="menu:profile"),
                InlineKeyboardButton(text="📜 History", callback_data="menu:history"),
            ],
            [
                InlineKeyboardButton(text="💳 Plans", callback_data="menu:plans"),
                InlineKeyboardButton(text="🔗 Referral", callback_data="menu:referral"),
            ],
            [InlineKeyboardButton(text="❓ Help", callback_data="menu:help")],
        ]
    )


def history_pagination_keyboard(offset: int, total: int, page_size: int = 5) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = []
    if offset > 0:
        buttons.append(
            InlineKeyboardButton(text="← Prev", callback_data=f"history:page:{offset - page_size}")
        )
    if offset + page_size < total:
        buttons.append(
            InlineKeyboardButton(text="Next →", callback_data=f"history:page:{offset + page_size}")
        )
    if not buttons:
        return InlineKeyboardMarkup(inline_keyboard=[])
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
