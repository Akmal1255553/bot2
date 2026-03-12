#!/usr/bin/env bash
set -e

echo "Starting deployment setup for AI Media Telegram Bot..."

# 1. Update and install system dependencies
echo "Installing system dependencies (Python, PostgreSQL, venv)..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib

# 2. Setup PostgreSQL database and user
echo "Setting up PostgreSQL database..."
# Creates botuser and ai_bot database. Ignore errors if they already exist.
sudo -u postgres psql -c "CREATE USER botuser WITH PASSWORD 'STRONG_PASSWORD_HERE';" || echo "User botuser already exists."
sudo -u postgres psql -c "CREATE DATABASE ai_bot OWNER botuser;" || echo "Database ai_bot already exists."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_bot TO botuser;" || true

# 3. Create virtual environment and install dependencies
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# 5. Setup .env file
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️ Action Required: Edit the .env file with your actual BOT_TOKEN, PROVIDER_TOKEN, and STABILITY_API_KEY."
fi

# 6. Setup systemd service
echo "Setting up systemd service..."
PROJECT_DIR=$(pwd)
# Replace placeholder /path/to/project with the actual project directory
sed "s|/path/to/project|${PROJECT_DIR}|g" deploy/ai-media-bot.service > /tmp/ai-media-bot.service
sudo mv /tmp/ai-media-bot.service /etc/systemd/system/ai-media-bot.service
sudo systemctl daemon-reload
sudo systemctl enable ai-media-bot.service

echo ""
echo "✅ Deployment setup complete!"
echo "Next steps:"
echo "1. Edit .env with your credentials:  nano .env"
echo "   Make sure to update DATABASE_URL with the password you set (or use the one in this script)."
echo "2. Start the bot:                    sudo systemctl start ai-media-bot.service"
echo "3. View logs:                        sudo journalctl -u ai-media-bot.service -f"
