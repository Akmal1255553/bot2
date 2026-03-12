from datetime import datetime

from config import get_settings
from database.models import GenerationHistory, Plan, User

from bot.keyboards.generation import RATIO_LABELS, STYLE_LABELS


def format_datetime(dt: datetime | None) -> str:
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def plan_badge(plan: Plan) -> str:
    badges = {Plan.FREE: "🆓", Plan.BASIC: "⭐", Plan.PRO: "💎"}
    return badges.get(plan, "")


def progress_bar(used: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "▓" * length
    filled = min(length, int(used / total * length))
    return "▓" * filled + "░" * (length - filled)


def remaining_images(user: User) -> int:
    settings = get_settings()
    if user.plan == Plan.BASIC:
        return max(0, settings.basic_monthly_images - user.images_used_this_month)
    if user.plan == Plan.PRO:
        return max(0, settings.pro_monthly_images - user.images_used_this_month)
    return max(0, user.free_images_left)


def usage_text(user: User) -> str:
    settings = get_settings()
    if user.plan == Plan.BASIC:
        return f"{user.images_used_this_month}/{settings.basic_monthly_images}"
    if user.plan == Plan.PRO:
        return f"{user.images_used_this_month}/{settings.pro_monthly_images}"
    used_total = max(0, settings.free_images_default - user.free_images_left)
    return f"{used_total}/{settings.free_images_default}"


def format_profile(user: User) -> str:
    settings = get_settings()
    badge = plan_badge(user.plan)
    remaining = remaining_images(user)

    if user.plan == Plan.BASIC:
        used = user.images_used_this_month
        total = settings.basic_monthly_images
    elif user.plan == Plan.PRO:
        used = user.images_used_this_month
        total = settings.pro_monthly_images
    else:
        used = max(0, settings.free_images_default - user.free_images_left)
        total = settings.free_images_default

    bar = progress_bar(used, total)

    return (
        f"{badge} <b>Your Profile</b>\n\n"
        f"📋 <b>Plan:</b> {user.plan.value}\n"
        f"🖼 <b>Remaining:</b> {remaining} images\n"
        f"📊 <b>Usage:</b> {used}/{total}\n"
        f"    {bar}\n"
        f"📅 <b>Expiry:</b> {format_datetime(user.subscription_expiry)}\n"
    )


def format_generation_caption(
    user: User, style: str, aspect_ratio: str, queue_name: str
) -> str:
    badge = plan_badge(user.plan)
    style_label = STYLE_LABELS.get(style, style)
    ratio_label = RATIO_LABELS.get(aspect_ratio, aspect_ratio)
    remaining = remaining_images(user)

    return (
        f"✅ <b>Image Generated</b>  ({queue_name} priority)\n\n"
        f"{badge} Plan: <b>{user.plan.value}</b>\n"
        f"🎨 Style: {style_label}\n"
        f"📐 Ratio: {ratio_label}\n"
        f"🖼 Remaining: <b>{remaining}</b> images"
    )


def format_history_entry(entry: GenerationHistory, index: int) -> str:
    style_label = STYLE_LABELS.get(entry.style, entry.style)
    ratio_label = RATIO_LABELS.get(entry.aspect_ratio, entry.aspect_ratio)
    prompt_short = entry.prompt[:60] + "…" if len(entry.prompt) > 60 else entry.prompt
    date_str = entry.created_at.strftime("%b %d, %H:%M") if entry.created_at else "?"

    return (
        f"<b>{index}.</b> {date_str}\n"
        f"    💬 <i>{prompt_short}</i>\n"
        f"    🎨 {style_label}  •  📐 {ratio_label}  •  {entry.plan_at_generation}"
    )
