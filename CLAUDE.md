# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deloculator — Telegram Mini App для расчёта стоимости заказов. Замена Excel-калькулятора.

## Tech Stack

- **Backend:** Python + FastAPI (Clean Architecture)
- **Database:** SQLite + SQLAlchemy + Alembic (миграции)
- **Frontend:** HTML5, Alpine.js, Tailwind CSS (CDN)
- **Интеграция:** Google Sheets API для синхронизации каталога

## Commands

```bash
# Первоначальная настройка
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

# Запуск backend
cd backend && uvicorn app.main:app --reload

# Тесты
cd backend && pytest                    # Все тесты
cd backend && pytest tests/unit/        # Только unit тесты
cd backend && pytest -v -k "test_name"  # Один тест
cd backend && pytest --cov=app          # С coverage

# Миграции БД (Alembic)
cd backend && alembic upgrade head                              # Применить
cd backend && alembic revision --autogenerate -m "Description"  # Создать новую
cd backend && alembic downgrade -1                              # Откатить

# Синхронизация каталога (или через кнопку 🔄 в UI)
curl -X POST -H "X-Auth-Password: password" http://localhost:8000/api/catalog/sync
```

## Clean Architecture

Зависимости направлены внутрь: `presentation → application → domain ← infrastructure`

```
backend/app/
├── domain/           # Ядро: сущности и интерфейсы (без зависимостей)
│   ├── entities/     # Project, ProjectItem, CatalogProduct
│   └── repositories/ # Абстрактные интерфейсы
├── application/      # Use Cases: бизнес-операции
│   ├── dto/          # Data Transfer Objects
│   └── use_cases/    # ProjectUseCases, CatalogUseCases
├── infrastructure/   # Реализации
│   ├── persistence/  # SQLAlchemy модели и репозитории
│   └── external/     # GoogleSheetsService
├── presentation/     # FastAPI routers и middleware
└── utils/            # Логирование, CSRF, password hashing
```

**Важно:** При изменении domain entities нужно также обновить:
- `infrastructure/persistence/models/` (ORM)
- `application/dto/`
- Создать миграцию Alembic

## Формулы расчёта (domain/entities/project.py)

```python
# Для позиции:
item.subtotal = base_price × quantity
item.total_cost = cost_price × quantity

# Для проекта:
subtotal = Σ(item.subtotal)
revenue = subtotal × (1 - discount/100) × (1 - tax/100)
profit = revenue - Σ(item.total_cost)
margin = profit / revenue × 100%
```

Скидка и налог — оба ВЫЧИТАЮТСЯ из суммы.

## Frontend

```
frontend/
├── index.html      # Список проектов — Alpine.js: dashboard()
├── project.html    # Редактор проекта — Alpine.js: projectEditor()
├── login.html      # Страница входа
├── css/custom.css  # Стили + CSS переменные Telegram
└── js/
    ├── api.js      # Fetch wrapper с X-Auth-Password
    ├── app.js      # Alpine.js компоненты
    └── telegram.js # Telegram WebApp интеграция
```

**Alpine.js особенности:**
- `x-show` НЕ работает надёжно внутри `x-for` — использовать `:class="condition ? 'hidden' : ''"`
- Для фокуса в модалках: `setTimeout(() => el.focus(), 100)` вместо `$nextTick`
- События: `@blur` надёжнее чем `@change` на мобильных

## Telegram Mini App

Интеграция через `telegram.js`:
- `tg.init()` — expand, theme, safe area
- `tg.hapticFeedback(type)` — вибрация
- `tg.showBackButton()` / `tg.hideBackButton()`

CSS переменные Telegram в `custom.css`:
- `--tg-bg-color`, `--tg-text-color`, `--tg-hint-color` и др.
- Tailwind классы переопределены для использования Telegram theme
- Для прозрачности границ использовать `rgba()`, НЕ `opacity`

## Аутентификация и безопасность

- Пароль в заголовке `X-Auth-Password`
- Поддержка bcrypt хешей (backward compatible с plain text)
- Rate limiting: 100 req/min глобально, 5 req/min для /api/catalog/sync
- CSRF токены для мутирующих операций
- Security headers (CSP, X-Frame-Options и др.)

## API Endpoints

**Projects:** `GET/POST /api/projects`, `GET/PUT/DELETE /api/projects/{id}`
**Items:** `POST/PATCH/DELETE /api/projects/{id}/items/{item_id}`
**Catalog:** `GET /api/catalog/search?q=`, `GET /api/catalog/grouped`, `POST /api/catalog/sync`
**Health:** `GET /api/health` (публичный)

## Deployment

- **Production:** https://delo.brdg.tools
- **Server:** Timeweb Cloud VPS (176.57.214.150), systemd service `delo-bot`
- **SSH:** `ssh root@176.57.214.150` (доступ настроен)
- **Server path:** `/opt/delo-bot`
- **Auto-deploy:** Push to `main` → GitHub Actions → SSH deploy + миграции

```bash
# На сервере
sudo journalctl -u delo-bot -f     # Логи
sudo systemctl restart delo-bot    # Перезапуск

# Ручной деплой
ssh root@176.57.214.150 "cd /opt/delo-bot && git pull && sudo systemctl restart delo-bot"
```

## CI/CD

- `.github/workflows/ci.yml` — тесты на каждый push/PR
- `.github/workflows/deploy.yml` — деплой при push в main
- Деплой включает: backup БД → git pull → pip install → alembic upgrade → restart

## Git

- GitHub: https://github.com/utkabotron/Delo-Bot
- Коммиты от pavelbrick@gmail.com
