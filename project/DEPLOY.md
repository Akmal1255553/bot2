# Production Deployment Guide — AI Media Telegram Bot

> Target: **Ubuntu 22.04 LTS** · No Docker · systemd · PostgreSQL 16

---

## 1. System Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install build tools (needed for asyncpg)
sudo apt install -y build-essential libpq-dev

# Install PostgreSQL 16
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-16
```

---

## 2. PostgreSQL Setup

```bash
sudo -u postgres psql
```

Inside the `psql` shell:

```sql
CREATE USER botdbuser WITH PASSWORD 'STRONG_DB_PASSWORD_HERE';
CREATE DATABASE ai_bot OWNER botdbuser;
GRANT ALL PRIVILEGES ON DATABASE ai_bot TO botdbuser;
\q
```

---

## 3. Create System User

```bash
sudo useradd --system --shell /usr/sbin/nologin --home-dir /opt/ai-media-bot botuser
```

---

## 4. Deploy Application Code

```bash
# Create application directory
sudo mkdir -p /opt/ai-media-bot
sudo mkdir -p /var/log/ai-media-bot

# Upload your project files to the server (from your local machine):
# scp -r ./project/* user@YOUR_SERVER_IP:/tmp/ai-media-bot/

# Copy files into place (on the server)
sudo cp -r /tmp/ai-media-bot/* /opt/ai-media-bot/

# Create virtual environment
sudo python3.11 -m venv /opt/ai-media-bot/venv

# Install dependencies
sudo /opt/ai-media-bot/venv/bin/pip install --upgrade pip
sudo /opt/ai-media-bot/venv/bin/pip install -r /opt/ai-media-bot/requirements.txt
```

---

## 5. Configure Environment

```bash
sudo cp /opt/ai-media-bot/.env.example /opt/ai-media-bot/.env
sudo nano /opt/ai-media-bot/.env
```

**Required edits in `.env`:**

| Variable | Value |
|---|---|
| `BOT_TOKEN` | Your Telegram bot token |
| `PROVIDER_TOKEN` | Your payment provider token |
| `ADMIN_IDS_RAW` | Comma-separated Telegram user IDs |
| `STABILITY_API_KEY` | Your Stability AI API key |
| `DATABASE_URL` | `postgresql+asyncpg://botdbuser:STRONG_DB_PASSWORD_HERE@localhost:5432/ai_bot` |

```bash
# Lock down .env permissions
sudo chmod 600 /opt/ai-media-bot/.env
```

---

## 6. Set File Ownership

```bash
sudo chown -R botuser:botuser /opt/ai-media-bot
sudo chown -R botuser:botuser /var/log/ai-media-bot
```

---

## 7. Install systemd Service

```bash
sudo cp /opt/ai-media-bot/deploy/ai-media-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-media-bot.service
sudo systemctl start ai-media-bot.service
```

---

## 8. Verify

```bash
# Check service status
sudo systemctl status ai-media-bot

# View live logs
sudo journalctl -u ai-media-bot -f

# Check log file
sudo tail -f /var/log/ai-media-bot/bot.log
```

---

## 9. Common Management Commands

```bash
# Restart the bot
sudo systemctl restart ai-media-bot

# Stop the bot
sudo systemctl stop ai-media-bot

# View recent logs (last 100 lines)
sudo journalctl -u ai-media-bot -n 100 --no-pager

# Check if auto-restart works
sudo systemctl kill ai-media-bot   # should restart within 5s
```

---

## 10. Firewall (Optional but Recommended)

```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

> **Note:** The bot only makes outgoing connections to Telegram API — no inbound ports need to be opened unless you use webhooks.

---

## 11. Updating the Bot

```bash
# Upload new code
# scp -r ./project/* user@YOUR_SERVER_IP:/tmp/ai-media-bot/

# Stop, update, restart
sudo systemctl stop ai-media-bot
sudo cp -r /tmp/ai-media-bot/* /opt/ai-media-bot/
sudo /opt/ai-media-bot/venv/bin/pip install -r /opt/ai-media-bot/requirements.txt
sudo chown -R botuser:botuser /opt/ai-media-bot
sudo systemctl start ai-media-bot
```

---

## 12. Log Rotation

The bot automatically rotates its own log files (10 MB max, 5 backups). For `journalctl` logs, you can limit disk usage:

```bash
sudo journalctl --vacuum-size=200M
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Service fails immediately | `journalctl -u ai-media-bot -n 50` — check for missing env vars or DB connection errors |
| `Permission denied` on log file | `sudo chown -R botuser:botuser /var/log/ai-media-bot` |
| DB connection refused | Verify PostgreSQL is running: `sudo systemctl status postgresql` |
| Bot not responding | Check `systemctl status ai-media-bot` — if `inactive`, restart |
