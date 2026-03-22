from __future__ import annotations

import secrets
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Plan(StrEnum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"


class Language(StrEnum):
    EN = "en"
    RU = "ru"
    UZ = "uz"


def _generate_referral_code() -> str:
    return secrets.token_urlsafe(6)[:8]


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("free_images_left >= 0", name="chk_free_images_nonnegative"),
        CheckConstraint("images_used_this_month >= 0", name="chk_images_used_nonnegative"),
        CheckConstraint("requests_in_window >= 0", name="chk_requests_window_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    plan: Mapped[Plan] = mapped_column(
        SqlEnum(Plan, native_enum=False, length=10),
        default=Plan.FREE,
        nullable=False,
        index=True,
    )
    language: Mapped[str | None] = mapped_column(String(2), nullable=True, default=None)
    free_images_left: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    images_used_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_period_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    request_window_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    requests_in_window: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    subscription_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Referral system
    referral_code: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, default=_generate_referral_code
    )
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None)
    referral_bonus_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    generations: Mapped[list[GenerationHistory]] = relationship(
        "GenerationHistory", back_populates="user", lazy="selectin"
    )


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str] = mapped_column(String(30), nullable=False, default="none")
    aspect_ratio: Mapped[str] = mapped_column(String(10), nullable=False, default="1:1")
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_at_generation: Mapped[str] = mapped_column(String(10), nullable=False, default="FREE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="generations")
