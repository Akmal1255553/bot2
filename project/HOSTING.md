# 24/7 Hosting Guide

This bot must run on a server that stays online when your PC is off. Below are
three recommended options ordered from easiest to most flexible.

For all options you will need to set these environment variables / secrets:

| Variable | Where to get it |
|---|---|
| `BOT_TOKEN` | https://t.me/BotFather → `/newbot` |
| `STABILITY_API_KEY` | https://platform.stability.ai/account/keys |
| `USDT_TRC20_WALLET` | Your TRON (TRC20) wallet address |
| `ADMIN_IDS_RAW` | Your Telegram numeric user ID (https://t.me/userinfobot) |
| `DATABASE_URL` | Provided automatically by the platform when you attach Postgres |

---

## Option 1 — Fly.io (recommended for free / low cost, always-on)

Fly.io keeps a small VM running 24/7. A `fly.toml` is included.

```bash
# 1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly auth signup        # or: fly auth login

cd project

# 2. Create the app (uses fly.toml in this folder)
fly launch --no-deploy --copy-config --name <your-unique-app-name>

# 3. Create a Postgres database and attach it
fly postgres create --name <your-unique-app-name>-db --region fra
fly postgres attach <your-unique-app-name>-db
# This sets DATABASE_URL on the app automatically.
# Note: the bot expects the asyncpg driver, so after attach, run:
fly secrets set DATABASE_URL="$(fly ssh console -C 'printenv DATABASE_URL' | tr -d '\r' | sed 's|^postgres://|postgresql+asyncpg://|; s|^postgresql://|postgresql+asyncpg://|')"

# 4. Set bot secrets
fly secrets set \
  BOT_TOKEN="123456:your_bot_token" \
  STABILITY_API_KEY="sk-..." \
  USDT_TRC20_WALLET="T..." \
  ADMIN_IDS_RAW="123456789"

# 5. Deploy
fly deploy

# 6. Watch logs
fly logs
```

To restart the bot later: `fly apps restart <your-app-name>`.

---

## Option 2 — Railway (easiest UI, free trial)

1. Push this repo to GitHub (already done).
2. Go to https://railway.app → **New Project → Deploy from GitHub** → pick `bot2`.
3. Set the **Root Directory** to `project`.
4. Add a **PostgreSQL** plugin in the same project. Railway will inject
   `DATABASE_URL`. Override it once with the asyncpg driver:
   `DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`
   (use the values from the Postgres plugin's `Connect` tab).
5. Add the other environment variables (see table above).
6. The included `Procfile` declares a `worker` process — Railway will run it.

---

## Option 3 — VPS (full control)

Follow [`DEPLOY.md`](./DEPLOY.md) for a step-by-step Ubuntu 22.04 + systemd
deployment. systemd ensures the bot auto-restarts on crash and on reboot.

The bot only makes outbound connections (long polling), so no inbound ports
need to be opened.

---

## Verifying it's running

After deploying, open Telegram and send `/start` to your bot. The first reply
confirms it's online. To monitor:

- Fly.io: `fly logs`
- Railway: project → service → **Logs** tab
- VPS: `sudo journalctl -u ai-media-bot -f`
