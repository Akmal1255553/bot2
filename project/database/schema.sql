CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    plan VARCHAR(10) NOT NULL DEFAULT 'FREE',
    free_images_left INTEGER NOT NULL DEFAULT 3,
    images_used_this_month INTEGER NOT NULL DEFAULT 0,
    subscription_expiry TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_free_images_nonnegative CHECK (free_images_left >= 0),
    CONSTRAINT chk_images_used_nonnegative CHECK (images_used_this_month >= 0),
    CONSTRAINT chk_plan_allowed CHECK (plan IN ('FREE', 'BASIC', 'PRO'))
);

CREATE INDEX IF NOT EXISTS ix_users_plan ON users(plan);
CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);
