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
# Запуск backend (из корня проекта)
cd backend && uvicorn app.main:app --reload

# Синхронизация каталога из Google Sheets
python scripts/sync_catalog.py

# Или через API
curl -X POST http://localhost:8000/api/catalog/sync
```

## Clean Architecture

Зависимости направлены внутрь: `presentation → application → domain ← infrastructure`

```
backend/app/
├── domain/           # Ядро: сущности и интерфейсы (без зависимостей)
├── application/      # Use Cases: бизнес-операции через интерфейсы domain
├── infrastructure/   # Реализации: SQLAlchemy, Google Sheets, Telegram
└── presentation/     # API: FastAPI routers, получают Use Cases через DI
```

**Domain** содержит бизнес-логику расчётов в entities (Project, ProjectItem). Репозитории — абстрактные интерфейсы.

**Infrastructure** реализует интерфейсы domain. При добавлении нового хранилища — создать новую реализацию IProjectRepository.

**Presentation** использует Dependency Injection через FastAPI Depends для получения Use Cases.

## Формулы расчёта (domain/entities/project.py)

```
Subtotal = Σ(base_price × quantity)
Revenue  = Subtotal × (1 - discount/100) × (1 - tax/100)
Cost     = Σ(cost_price × quantity)
Profit   = Revenue - Cost
Margin   = Profit / Revenue × 100%
```

Скидка и налог — оба вычитаются из суммы.

## Google Sheets

Каталог синхронизируется из листа "Справочник Изделий":
- Колонка C: Название, D: Тип, Q: Себестоимость, R: База (цена)
- Настройки в `infrastructure/external/google_sheets.py`

## Аутентификация

Простая аутентификация по паролю:
- Пароль задаётся в `config.py` → `app_password` (по умолчанию: `deloculator2024`)
- Frontend хранит пароль в `localStorage` и отправляет в заголовке `X-Auth-Password`
- AuthMiddleware защищает только `/api/*` эндпоинты (кроме `/api/health`)
- HTML-страницы публичные, но делают редирект на `/login` если нет пароля в localStorage

## Frontend

```
frontend/
├── index.html      # Список проектов (dashboard)
├── project.html    # Редактор проекта
├── login.html      # Страница входа
└── js/
    ├── api.js      # API клиент (fetch wrapper)
    ├── app.js      # Alpine.js компоненты (dashboard, projectEditor)
    └── telegram.js # Telegram WebApp интеграция
```

## API Endpoints

- `GET/POST /api/projects` — список/создание проектов
- `GET/PUT/DELETE /api/projects/{id}` — операции с проектом
- `POST/DELETE/PATCH /api/projects/{id}/items` — позиции проекта
- `GET /api/catalog/search?q=` — поиск в каталоге
- `GET /api/catalog/grouped` — каталог сгруппированный по названию
- `POST /api/catalog/sync` — синхронизация с Google Sheets

## Git Configuration

- GitHub account: pavelbrick@gmail.com
