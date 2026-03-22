from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import ratio_label, style_label

STYLE_IDS = [
    "realistic",
    "anime",
    "digital_art",
    "oil_painting",
    "watercolor",
    "3d_render",
    "pixel_art",
    "none",
]

STYLE_PROMPTS = {
    "realistic": "photorealistic, highly detailed",
    "anime": "anime style, vibrant colors, detailed illustration",
    "digital_art": "digital art, concept art, highly detailed",
    "oil_painting": "oil painting style, textured brushstrokes, fine art",
    "watercolor": "watercolor painting, soft colors, artistic",
    "3d_render": "3D render, octane render, highly detailed",
    "pixel_art": "pixel art style, retro game aesthetic, 8-bit",
    "none": "",
}

ASPECT_RATIO_IDS = ["1:1", "9:16", "16:9"]


def style_picker_keyboard(language: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for index in range(0, len(STYLE_IDS), 2):
        chunk = STYLE_IDS[index : index + 2]
        row = [
            InlineKeyboardButton(
                text=style_label(language, style_id),
                callback_data=f"style:{style_id}",
            )
            for style_id in chunk
        ]
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def aspect_ratio_keyboard(language: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=ratio_label(language, ratio_id),
            callback_data=f"ratio:{ratio_id}",
        )
        for ratio_id in ASPECT_RATIO_IDS
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
