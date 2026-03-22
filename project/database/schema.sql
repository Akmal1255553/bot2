CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    plan VARCHAR(10) NOT NULL DEFAULT 'FREE',
    language VARCHAR(2) NULL,
    free_images_left INTEGER NOT NULL DEFAULT 3,
    images_used_this_month INTEGER NOT NULL DEFAULT 0,
    usage_period_started_at TIMESTAMPTZ NULL,
    request_window_started_at TIMESTAMPTZ NULL,
    requests_in_window INTEGER NOT NULL DEFAULT 0,
    subscription_expiry TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    referral_code VARCHAR(16) NOT NULL UNIQUE,
    referred_by BIGINT NULL,
    referral_bonus_earned INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT chk_free_images_nonnegative CHECK (free_images_left >= 0),
    CONSTRAINT chk_images_used_nonnegative CHECK (images_used_this_month >= 0),
    CONSTRAINT chk_requests_window_nonnegative CHECK (requests_in_window >= 0),
    CONSTRAINT chk_plan_allowed CHECK (plan IN ('FREE', 'BASIC', 'PRO'))
);

CREATE TABLE IF NOT EXISTS generation_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    prompt TEXT NOT NULL,
    style VARCHAR(30) NOT NULL DEFAULT 'none',
    aspect_ratio VARCHAR(10) NOT NULL DEFAULT '1:1',
    image_url TEXT NULL,
    plan_at_generation VARCHAR(10) NOT NULL DEFAULT 'FREE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_plan ON users(plan);
CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS ix_users_language ON users(language);
CREATE INDEX IF NOT EXISTS ix_generation_history_user_id ON generation_history(user_id);
