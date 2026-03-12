# AI Image Telegram Bot

Telegram bot for image generation with Stability AI, PostgreSQL, aiogram, and Telegram Payments.

## Local Run (No Docker)

1. Install Python `3.11+` and PostgreSQL `14+`.
2. Create DB:
   - `createdb ai_bot`
3. Copy env file:
   - `copy .env.example .env` (Windows)
4. Fill required variables in `.env`:
   - `BOT_TOKEN`
   - `PROVIDER_TOKEN`
   - `STABILITY_API_KEY`
5. Ensure DB URL points to localhost:
   - `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_bot`
6. Install deps:
   - `pip install -r requirements.txt`
7. Start bot:
   - `python main.py`

## Database Initialization

- On startup, `main.py` calls `init_db()`.
- Tables are auto-created if they do not exist (`Base.metadata.create_all`).
- Optional SQL schema is available in `database/schema.sql`.

## Payments

- Plans: `BASIC` and `PRO`
- Currency: `USD`
- Amounts are passed in cents (smallest currency unit)
- Handled updates:
  - `pre_checkout_query`
  - `successful_payment`

## Commands

- `/start`
- `/generate_image`
- `/profile`
- `/buy`
- `/help`
- `/admin`
