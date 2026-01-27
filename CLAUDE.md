# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deloculator — Telegram Mini App для расчёта стоимости заказов. Замена Excel-калькулятора.

## Tech Stack

- **Backend:** Python + FastAPI (Clean Architecture)
- **Database:** SQLite + SQLAlchemy
- **Frontend:** HTML5, Alpine.js, Tailwind CSS (CDN)
- **Интеграция:** Google Sheets API для синхронизации каталога

## Commands

```bash
# Первоначальная настройка
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Создать .env файл (скопировать из backend/.env.example)
cp backend/.env.example backend/.env
# Настроить TELEGRAM_BOT_TOKEN, APP_PASSWORD, и credentials.json для Google Sheets

# Запуск backend для разработки (из корня проекта)
cd backend && uvicorn app.main:app --reload

# Или из корня без cd
uvicorn backend.app.main:app --reload

# Синхронизация каталога из Google Sheets
python scripts/sync_catalog.py

# Или через API
curl -X POST -H "X-Auth-Password: your_password" http://localhost:8000/api/catalog/sync

# Проверка здоровья API
curl http://localhost:8000/api/health
```

## Clean Architecture

Зависимости направлены внутрь: `presentation → application → domain ← infrastructure`

```
backend/app/
├── domain/                    # Ядро: сущности и интерфейсы (без зависимостей)
│   ├── entities/             # Project, ProjectItem, CatalogProduct
│   └── repositories/         # Абстрактные интерфейсы (IProjectRepository, ICatalogRepository)
├── application/               # Use Cases: бизнес-операции через интерфейсы domain
│   ├── dto/                  # Data Transfer Objects для API
│   └── use_cases/            # ProjectUseCases, CatalogUseCases
├── infrastructure/            # Реализации: SQLAlchemy, Google Sheets, Telegram
│   ├── persistence/          # SQLAlchemy модели и репозитории
│   │   ├── models/           # ProjectModel, CatalogProductModel (ORM)
│   │   └── repositories/     # SQLAlchemy реализации интерфейсов domain
│   └── external/             # GoogleSheetsService, TelegramService
└── presentation/              # API: FastAPI routers, получают Use Cases через DI
    ├── api/                  # projects.py, catalog.py (routers)
    └── middleware/           # AuthMiddleware, TelegramMiddleware
```

**Domain** содержит бизнес-логику расчётов в entities (Project, ProjectItem). Репозитории — абстрактные интерфейсы.

**Infrastructure** реализует интерфейсы domain. При добавлении нового хранилища — создать новую реализацию IProjectRepository.

**Presentation** использует Dependency Injection через FastAPI Depends для получения Use Cases.

**Важно:** При изменении domain entities также нужно обновить infrastructure/persistence/models (ORM) и application/dto.

## Формулы расчёта (domain/entities/project.py)

```python
# Для каждой позиции (ProjectItem):
item.subtotal = base_price × quantity
item.total_cost = cost_price × quantity

# Для проекта (Project):
subtotal = Σ(item.subtotal)                                    # Сумма всех позиций
revenue = subtotal × (1 - discount/100) × (1 - tax/100)       # С учётом скидки и налога
total_cost = Σ(item.total_cost)                                # Общая себестоимость
profit = revenue - total_cost                                   # Чистая прибыль
margin = (profit / revenue) × 100%                             # Рентабельность
```

**Важно:** Скидка (`global_discount`) и налог (`global_tax`) — оба ВЫЧИТАЮТСЯ из суммы (оба множителя < 1).

## Google Sheets

Каталог синхронизируется из листа "Справочник Изделий":
- **ID таблицы:** `18vDpWaCYA1rFhsyb54JhXXtR2b7RVsRplpiWZ93g1N8`
- **Колонки:** C = Название, D = Тип, Q = Себестоимость, R = База (цена)
- **Настройки:** `infrastructure/external/google_sheets.py`
- **Credentials:** Требуется файл `credentials.json` от Google Service Account в корне проекта
- **Синхронизация:** Можно запускать вручную через `scripts/sync_catalog.py` или через API

## Аутентификация

Простая аутентификация по паролю:
- Пароль задаётся в `config.py` → `app_password` (по умолчанию: `deloculator2024`)
- Frontend хранит пароль в `localStorage` и отправляет в заголовке `X-Auth-Password`
- AuthMiddleware защищает только `/api/*` эндпоинты (кроме `/api/health`)
- HTML-страницы публичные, но делают редирект на `/login` если нет пароля в localStorage

## Frontend

```
frontend/
├── index.html      # Список проектов (dashboard) — Alpine.js component: dashboardApp
├── project.html    # Редактор проекта — Alpine.js component: projectEditor
├── login.html      # Страница входа — проверка пароля, редирект
├── css/custom.css  # Кастомные стили + CSS переменные Telegram (--tg-theme-*)
└── js/
    ├── api.js      # API клиент: fetch wrapper с X-Auth-Password header
    ├── app.js      # Alpine.js компоненты:
    │               # - dashboardApp: список проектов, создание/удаление
    │               # - projectEditor: редактирование проекта, добавление позиций, расчёты
    └── telegram.js # Telegram WebApp интеграция (tg.init, haptic, safe area)
```

**Alpine.js компоненты:**
- `dashboardApp` — управление списком проектов (загрузка, создание, удаление)
- `projectEditor` — редактирование проекта (метаданные, позиции, поиск по каталогу)
- Все расчёты (subtotal, revenue, profit, margin) происходят реактивно на клиенте

## Telegram Mini App

Интеграция через `telegram.js`:
- `tg.init()` — инициализация (expand, theme, safe area)
- `tg.applySafeArea()` — отступы под системные элементы Telegram
- `tg.hapticFeedback(type)` — вибрация (light/medium/heavy/success/error)
- `tg.showBackButton()` / `tg.hideBackButton()` — кнопка "назад"

Настройка бота в @BotFather:
- `/mybots` → выбрать бота → **Mini Apps** → **Menu Button**
- URL: `https://delo.brdg.tools`

Токен бота хранится в `.env` → `TELEGRAM_BOT_TOKEN`

## API Endpoints

**Projects:**
- `GET /api/projects` — список всех проектов
- `POST /api/projects` — создание нового проекта
- `GET /api/projects/{id}` — получение проекта с позициями
- `PUT /api/projects/{id}` — обновление метаданных проекта
- `DELETE /api/projects/{id}` — удаление проекта

**Project Items:**
- `POST /api/projects/{id}/items` — добавление позиции
- `PATCH /api/projects/{project_id}/items/{item_id}` — обновление позиции (quantity)
- `DELETE /api/projects/{project_id}/items/{item_id}` — удаление позиции

**Catalog:**
- `GET /api/catalog/search?q=название` — поиск по названию (для автодополнения)
- `GET /api/catalog/grouped` — каталог, сгруппированный по названию
- `POST /api/catalog/sync` — синхронизация с Google Sheets (требует X-Auth-Password)

**Health:**
- `GET /api/health` — проверка состояния API (публичный, без авторизации)

## Deployment

- **Production URL:** https://delo.brdg.tools
- **Server:** Timeweb Cloud VPS (176.57.214.150)
- **Auto-deploy:** Push to `main` → GitHub Actions (.github/workflows/deploy.yml) → SSH deploy
- **Server path:** `/opt/delo-bot`
- **Systemd service:** `delo-bot.service`

**GitHub Actions Workflow:**
1. Push в `main` триггерит deploy.yml
2. SSH подключение к серверу (используя secrets: SERVER_HOST, SERVER_USER, SERVER_PASSWORD)
3. `git pull origin main`
4. `pip install -r backend/requirements.txt`
5. `sudo systemctl restart delo-bot`

Полезные команды на сервере:
```bash
sudo journalctl -u delo-bot -f     # Логи в реальном времени
sudo systemctl restart delo-bot    # Перезапуск сервиса
sudo systemctl status delo-bot     # Статус сервиса
curl -X POST -H 'X-Auth-Password: PASSWORD' http://127.0.0.1:8000/api/catalog/sync  # Синхронизация каталога
```

## Важные детали реализации

**Database:**
- SQLite база данных создаётся автоматически при первом запуске в `data/deloculator.db`
- Таблицы создаются через `Base.metadata.create_all()` в `app/main.py`
- Используется SQLAlchemy ORM с декларативным стилем

**Dependencies:**
- Все Python зависимости в `backend/requirements.txt`
- Frontend использует CDN: Alpine.js, Tailwind CSS — нет npm/webpack
- Google Sheets API требует отдельной настройки credentials.json

**Environment Variables (.env):**
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather
- `APP_PASSWORD` — пароль для доступа к API (по умолчанию: deloculator2024)
- `GOOGLE_SHEETS_ID` — ID таблицы Google Sheets
- `GOOGLE_CREDENTIALS_FILE` — путь к credentials.json
- `CORS_ORIGINS` — разрешённые origins для CORS

**Static Files:**
- Backend отдаёт статику из `/frontend` через `StaticFiles` и `FileResponse`
- CSS и JS монтируются как `/css` и `/js`
- HTML страницы отдаются через routes: `/`, `/login`, `/project/{id}`

## Git Configuration

- GitHub: https://github.com/utkabotron/Delo-Bot (public)
- GitHub account: pavelbrick@gmail.com
- **Важно:** Все коммиты должны быть от pavelbrick@gmail.com
