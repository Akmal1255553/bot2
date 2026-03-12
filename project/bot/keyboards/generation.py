from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ART_STYLES = [
    ("🎨 Realistic", "style:realistic"),
    ("🌸 Anime", "style:anime"),
    ("💻 Digital Art", "style:digital_art"),
    ("🖌️ Oil Painting", "style:oil_painting"),
    ("🎨 Watercolor", "style:watercolor"),
    ("🧊 3D Render", "style:3d_render"),
    ("👾 Pixel Art", "style:pixel_art"),
    ("✨ No Style", "style:none"),
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

STYLE_LABELS = {
    "realistic": "🎨 Realistic",
    "anime": "🌸 Anime",
    "digital_art": "💻 Digital Art",
    "oil_painting": "🖌️ Oil Painting",
    "watercolor": "🎨 Watercolor",
    "3d_render": "🧊 3D Render",
    "pixel_art": "👾 Pixel Art",
    "none": "✨ No Style",
}

ASPECT_RATIOS = [
    ("⬜ 1:1 Square", "ratio:1:1"),
    ("📱 9:16 Portrait", "ratio:9:16"),
    ("🖥️ 16:9 Landscape", "ratio:16:9"),
]

RATIO_LABELS = {
    "1:1": "⬜ Square",
    "9:16": "📱 Portrait",
    "16:9": "🖥️ Landscape",
}


def style_picker_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(ART_STYLES), 2):
        row = [InlineKeyboardButton(text=t, callback_data=d) for t, d in ART_STYLES[i : i + 2]]
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def aspect_ratio_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=d) for t, d in ASPECT_RATIOS]
        ]
    )
