from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-media-telegram-bot"
    log_level: str = "INFO"
    timezone: str = "UTC"
    log_file_path: str = "logs/bot.log"
    log_max_bytes: int = 10_485_760
    log_backup_count: int = 5

    bot_token: str = Field(min_length=10)
    provider_token: str = Field(min_length=1)
    admin_ids_raw: str = ""
    currency: str = "USD"
    basic_plan_price_cents: int = 700
    pro_plan_price_cents: int = 1500

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_bot"
    )

    stability_api_key: str = ""
    stability_credit_price_usd: float = 0.005
    stability_max_image_cost_usd: float = 0.015
    stability_core_credits: float = 3.0

    request_timeout_seconds: int = 60
    provider_timeout_retries: int = 2
    generation_max_prompt_len: int = 350
    banned_words_raw: str = "nsfw,terrorism,gore"

    free_images_default: int = 3
    basic_monthly_images: int = 80
    pro_monthly_images: int = 250
    subscription_days: int = 30
    referral_bonus_images: int = 2

    per_user_rate_limit_seconds: int = 10
    global_rate_limit_requests: int = 150
    global_rate_limit_period_seconds: int = 10
    global_generation_concurrency: int = 2
    daily_global_generation_cap: int = 500

    @field_validator("admin_ids_raw")
    @classmethod
    def strip_admin_ids(cls, v: str) -> str:
        return v.strip()

    @field_validator("stability_api_key")
    @classmethod
    def validate_stability_api_key(cls, v: str) -> str:
        token = v.strip()
        if not token:
            raise ValueError("STABILITY_API_KEY must not be empty")
        return token

    @field_validator("provider_token")
    @classmethod
    def validate_provider_token(cls, v: str) -> str:
        token = v.strip()
        if not token:
            raise ValueError("PROVIDER_TOKEN must not be empty")
        return token

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        currency = v.strip()
        if not currency:
            raise ValueError("CURRENCY must not be empty")
        if currency != currency.upper():
            raise ValueError("CURRENCY must be uppercase")
        return currency

    @field_validator("basic_plan_price_cents", "pro_plan_price_cents")
    @classmethod
    def validate_plan_prices(cls, v: int) -> int:
        if not isinstance(v, int):
            raise ValueError("Plan price must be an integer amount in cents")
        if v <= 0:
            raise ValueError("Plan price must be greater than 0")
        return v

    @field_validator("subscription_days")
    @classmethod
    def validate_subscription_days(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("SUBSCRIPTION_DAYS must be greater than 0")
        return v

    @field_validator("banned_words_raw")
    @classmethod
    def strip_banned_words(cls, v: str) -> str:
        return v.strip()

    @property
    def admin_ids(self) -> set[int]:
        if not self.admin_ids_raw:
            return set()
        return {int(x.strip()) for x in self.admin_ids_raw.split(",") if x.strip()}

    @property
    def banned_words(self) -> set[str]:
        if not self.banned_words_raw:
            return set()
        return {x.strip().lower() for x in self.banned_words_raw.split(",") if x.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
