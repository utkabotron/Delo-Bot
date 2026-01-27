#!/bin/bash
# Скрипт первоначальной настройки сервера
# Запускать один раз: sudo bash setup-server.sh YOUR_DOMAIN

set -e

DOMAIN=$1
APP_DIR="/opt/delo-bot"

if [ -z "$DOMAIN" ]; then
    echo "Usage: sudo bash setup-server.sh YOUR_DOMAIN"
    exit 1
fi

echo "=== Installing dependencies ==="
apt update
apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git

echo "=== Cloning repository ==="
if [ -d "$APP_DIR" ]; then
    echo "Directory exists, pulling updates..."
    cd $APP_DIR && git pull origin main
else
    git clone https://github.com/utkabotron/Delo-Bot.git $APP_DIR
fi

echo "=== Setting up Python virtual environment ==="
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== Creating .env file ==="
if [ ! -f "$APP_DIR/backend/.env" ]; then
    cp $APP_DIR/backend/.env.example $APP_DIR/backend/.env
    echo "IMPORTANT: Edit $APP_DIR/backend/.env with your settings!"
fi

echo "=== Setting permissions ==="
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

echo "=== Installing systemd service ==="
cp $APP_DIR/deploy/delo-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable delo-bot

echo "=== Configuring Nginx ==="
sed "s/YOUR_DOMAIN/$DOMAIN/g" $APP_DIR/deploy/nginx.conf > /etc/nginx/sites-available/delo-bot
ln -sf /etc/nginx/sites-available/delo-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "=== Setting up SSL certificate ==="
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
    echo "Certbot failed. Run manually: sudo certbot --nginx -d $DOMAIN"
}

echo "=== Starting application ==="
systemctl start delo-bot
systemctl status delo-bot --no-pager

echo ""
echo "=== Setup complete! ==="
echo "1. Edit /opt/delo-bot/backend/.env with your settings"
echo "2. Add credentials.json for Google Sheets"
echo "3. Restart: sudo systemctl restart delo-bot"
echo "4. View logs: sudo journalctl -u delo-bot -f"
echo ""
echo "Your app will be available at: https://$DOMAIN"
