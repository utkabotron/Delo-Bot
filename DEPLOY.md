# Деплой Delo-Bot

## Шаг 1: Настройка GitHub Secrets

В репозитории GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Добавь три секрета:

| Секрет | Значение |
|--------|----------|
| `SERVER_HOST` | IP адрес или домен сервера |
| `SERVER_USER` | Имя пользователя SSH (например, `root`) |
| `SERVER_PASSWORD` | Пароль SSH |

## Шаг 2: Первоначальная настройка сервера

Подключись к серверу по SSH и выполни:

```bash
# Скачать и запустить скрипт настройки
curl -O https://raw.githubusercontent.com/utkabotron/Delo-Bot/main/deploy/setup-server.sh
sudo bash setup-server.sh your-domain.com
```

Или вручную:

```bash
# Установить зависимости
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git

# Клонировать репозиторий
sudo git clone https://github.com/utkabotron/Delo-Bot.git /opt/delo-bot
cd /opt/delo-bot

# Создать виртуальное окружение
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r backend/requirements.txt

# Настроить .env
sudo cp backend/.env.example backend/.env
sudo nano backend/.env  # Редактировать настройки

# Скопировать credentials.json для Google Sheets (если нужно)
# scp credentials.json user@server:/opt/delo-bot/backend/

# Установить systemd сервис
sudo cp deploy/delo-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable delo-bot
sudo systemctl start delo-bot

# Настроить nginx
sudo sed 's/YOUR_DOMAIN/your-domain.com/g' deploy/nginx.conf > /etc/nginx/sites-available/delo-bot
sudo ln -sf /etc/nginx/sites-available/delo-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Получить SSL сертификат
sudo certbot --nginx -d your-domain.com
```

## Шаг 3: Настройка .env на сервере

Отредактируй `/opt/delo-bot/backend/.env`:

```bash
sudo nano /opt/delo-bot/backend/.env
```

Важные параметры:
- `APP_PASSWORD` - пароль для входа в приложение
- `GOOGLE_SHEETS_ID` - ID таблицы Google Sheets

## Шаг 4: Права доступа

```bash
sudo chown -R www-data:www-data /opt/delo-bot
sudo chmod -R 755 /opt/delo-bot
```

## Автоматический деплой

После настройки, каждый push в `main` ветку автоматически деплоит изменения:

1. GitHub Action подключается по SSH
2. Делает `git pull`
3. Обновляет зависимости
4. Перезапускает сервис

## Полезные команды

```bash
# Логи приложения
sudo journalctl -u delo-bot -f

# Статус сервиса
sudo systemctl status delo-bot

# Перезапуск
sudo systemctl restart delo-bot

# Логи nginx
sudo tail -f /var/log/nginx/error.log
```

## Устранение проблем

**Сервис не запускается:**
```bash
sudo journalctl -u delo-bot -n 50 --no-pager
```

**502 Bad Gateway:**
- Проверь что сервис запущен: `sudo systemctl status delo-bot`
- Проверь порт: `curl http://127.0.0.1:8000/api/health`

**Permission denied:**
```bash
sudo chown -R www-data:www-data /opt/delo-bot
```
