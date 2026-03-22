# AI Image Telegram Bot

Telegram bot for image generation with Stability AI, PostgreSQL, aiogram, crypto plan purchase flow, and built-in i18n (EN/RU/UZ).

## Local Run (No Docker)

1. Install Python `3.11+` and PostgreSQL `14+`.
2. Create DB:
   - `createdb ai_bot`
3. Copy env file:
   - `copy .env.example .env` (Windows)
4. Fill required variables in `.env`:
   - `BOT_TOKEN`
   - `STABILITY_API_KEY`
   - `USDT_TRC20_WALLET`
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

## Plans and Payments

- `FREE`: 3 images
- `BASIC`: 50 images/month, `2.99 USDT`
- `PRO`: 200 images/month, `6.99 USDT`
- Payment flow is crypto MVP:
  - user taps `Buy Basic` or `Buy Pro`
  - bot shows USDT TRC20 payment instructions
  - user taps `I Paid`
  - bot sends request to admin for manual approval
  - admin approves via button or `/admin plan <id> <BASIC|PRO>`

## Localization

- Language selection on `/start`
- Supported languages:
  - English
  - Russian
  - Uzbek
- User language is stored in DB and used for all bot messages

## Commands

- `/start`
- `/generate_image`
- `/profile`
- `/buy`
- `/help`
- `/admin`
