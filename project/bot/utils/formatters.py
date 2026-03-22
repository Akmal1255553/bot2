from __future__ import annotations

from datetime import datetime

from config import get_settings
from database.models import GenerationHistory, Plan, User

from bot.i18n import plan_label, ratio_label, style_label, t


def format_datetime(dt: datetime | None, language: str) -> str:
    if not dt:
        return t(language, "profile.not_available")
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def plan_badge(plan: Plan) -> str:
    badges = {Plan.FREE: "FREE", Plan.BASIC: "BASIC", Plan.PRO: "PRO"}
    return badges.get(plan, "")


def progress_bar(used: int, total: int, length: int = 10) -> str:
    if total <= 0:
        return "#" * length
    filled = min(length, int(used / total * length))
    return "#" * filled + "-" * (length - filled)


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


def format_profile(user: User, language: str) -> str:
    settings = get_settings()
    remaining = remaining_images(user)
    plan_text = plan_label(language, user.plan.value)

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
        f"{t(language, 'profile.title')}\n\n"
        f"{t(language, 'profile.plan')} <b>{plan_text}</b>\n"
        f"{t(language, 'profile.remaining')} <b>{remaining}</b>\n"
        f"{t(language, 'profile.usage')} <b>{used}/{total}</b>\n"
        f"{bar}\n"
        f"{t(language, 'profile.expiry')} <b>{format_datetime(user.subscription_expiry, language)}</b>"
    )


def format_generation_caption(
    user: User,
    style: str,
    aspect_ratio: str,
    queue_name: str,
    language: str,
) -> str:
    remaining = remaining_images(user)
    queue_label = t(language, f"queue.{queue_name}")
    return t(
        language,
        "generation.caption",
        queue=queue_label,
        plan=plan_label(language, user.plan.value),
        style=style_label(language, style),
        ratio=ratio_label(language, aspect_ratio),
        remaining=remaining,
    )


def format_history_entry(entry: GenerationHistory, index: int, language: str) -> str:
    prompt_short = entry.prompt[:60] + "..." if len(entry.prompt) > 60 else entry.prompt
    date_str = entry.created_at.strftime("%b %d, %H:%M") if entry.created_at else "?"
    return t(
        language,
        "history.entry",
        index=index,
        date=date_str,
        prompt=prompt_short,
        style=style_label(language, entry.style),
        ratio=ratio_label(language, entry.aspect_ratio),
        plan=plan_label(language, entry.plan_at_generation),
    )
