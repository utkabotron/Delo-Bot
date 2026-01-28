# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deloculator — Telegram Mini App для расчёта стоимости заказов. Замена Excel-калькулятора.

## Tech Stack

- **Backend:** Python + FastAPI (Clean Architecture)
- **Database:** SQLite + SQLAlchemy + Alembic (миграции)
- **Frontend:** HTML5, Alpine.js, Tailwind CSS (CDN)
- **PDF:** ReportLab (с Cyrillic-шрифтами)
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

# Деплой
ssh root@176.57.214.150 "cd /opt/delo-bot && git pull && sudo systemctl restart delo-bot"

# Логи на сервере
ssh root@176.57.214.150 "journalctl -u delo-bot -f"
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

**Экспорт для клиента** (без себестоимости/прибыли/налога):
```python
client_total = subtotal × (1 - discount/100)  # Налог НЕ показываем клиенту
```

## Frontend Layout Architecture

Две страницы используют **разные layout-подходы** — это критично для скролла:

**index.html (dashboard)** — header внутри скролл-контейнера:
```
<body overflow-hidden, height: 100dvh>
  <main h-full overflow-y-auto native-scroll>   ← единый скролл
    <header sticky top-0 header-gradient>        ← прилипает при скролле
    </header>
    контент скроллится ПОД header
  </main>
  модалки (fixed, вне main)
</body>
```

**project.html** — header вне скролл-контейнера:
```
<body flex flex-col overflow-hidden, height: 100dvh>
  <header flex-shrink-0>                         ← не скроллится
  </header>
  <main flex-1 overflow-y-auto native-scroll>    ← скроллится отдельно
  </main>
  <div fixed bottom-0 ios26-summary>             ← панель итогов
  </div>
  модалки (fixed, вне main)
</body>
```

**Ключевые CSS-паттерны скролла (custom.css):**
- `html, body { overscroll-behavior: none }` — отключает bounce на body
- `.native-scroll` — включает iOS bounce обратно через `overscroll-behavior-y: auto` + `-webkit-overflow-scrolling: touch`
- Модалки при открытии блокируют скролл main через `:class="showModal && 'overflow-hidden'"`
- Модалки с длинным контентом: `max-h-[80vh] overflow-y-auto overscroll-contain`

## Frontend

```
frontend/
├── index.html      # Dashboard: 3 таба (Активные/Архив/Каталог) — Alpine.js: dashboard()
├── project.html    # Редактор проекта + экспорт — Alpine.js: projectEditor()
├── login.html      # Страница входа
├── css/custom.css  # iOS 26 стили + CSS переменные Telegram
└── js/
    ├── api.js      # Fetch wrapper с X-Auth-Password
    ├── app.js      # Alpine.js компоненты
    └── telegram.js # Telegram WebApp интеграция
```

**Alpine.js особенности:**
- `x-show` НЕ работает надёжно внутри `x-for` — использовать `:class="condition ? 'hidden' : ''"`
- Для фокуса в модалках: `setTimeout(() => el.focus(), 100)` вместо `$nextTick`
- События: `@blur` надёжнее чем `@change` на мобильных

## iOS 26 Style Classes (custom.css)

Приложение использует стили в духе iOS 26 / Apple HIG:

- `.header-gradient` — градиент сверху (непрозрачный) → снизу (прозрачный), контент уходит под него
- `.grouped-list` — карточки со скруглением 20px, `.grouped-list-item` + `.grouped-list-divider`
- `.ios26-inset` — margin 16px от краёв экрана
- `.ios26-modal` / `.ios26-modal-bottom` — модалки со скруглением 20px
- `.ios26-summary` — fixed bottom panel со скруглением 20px 20px 0 0, тень вверх
- `.ios26-input` / `.ios26-button` — скругление 12px
- `.native-scroll` — нативный iOS bounce-скролл

**Apple HIG принципы:**
- Touch targets минимум 44×44 points
- Скругления: контейнеры 20px, кнопки/инпуты 12px
- Кнопки в модалках: full-width, stacked vertically (`space-y-3`)

## Каталог и себестоимость

CatalogProduct имеет 12 компонентов себестоимости (синхронизируются из Google Sheets):
```
materials, metal, powder, cnc, carpentry, painting,
upholstery, components, box, logistics, assembly, other
```

Dashboard tab "Каталог" показывает все товары с фильтрами:
- Dropdown по названию (base_name) + зависимый dropdown по типу (product_type)
- Модалка детали с разбивкой себестоимости (показывает только ненулевые компоненты)

## Telegram Mini App

Интеграция через `telegram.js`:
- `tg.init()` — expand, disableVerticalSwipes, theme, safe area
- `tg.hapticFeedback(type)` — вибрация (light, medium, heavy, success, error)
- `tg.showBackButton()` / `tg.hideBackButton()`
- `tg.applySafeArea()` — читает `contentSafeAreaInset` и применяет padding к headers

CSS переменные Telegram в `custom.css`:
- `--tg-bg-color`, `--tg-text-color`, `--tg-hint-color` и др.
- Tailwind классы переопределены для использования Telegram theme
- Для прозрачности границ использовать `rgba()`, НЕ `opacity`

## Аутентификация и безопасность

- Пароль в заголовке `X-Auth-Password`
- Поддержка bcrypt хешей (backward compatible с plain text)
- Rate limiting: 100 req/min глобально, 5 req/min для /api/catalog/sync
- CSRF токены для мутирующих операций
- Security headers (CSP с `'unsafe-inline'` для Alpine.js)

## API Endpoints

**Projects:** `GET/POST /api/projects`, `GET/PUT/DELETE /api/projects/{id}`
- `GET /api/projects?archived=true` — только архивные
- `GET /api/projects/{id}/export?format=text|pdf` — экспорт для клиента

**Items:** `POST/PATCH/DELETE /api/projects/{id}/items/{item_id}`
**Catalog:** `GET /api/catalog/search?q=`, `GET /api/catalog/grouped`, `POST /api/catalog/sync`
**Health:** `GET /api/health` (публичный)

## Deployment

- **Production:** https://delo.brdg.tools
- **Server:** Timeweb Cloud VPS (176.57.214.150), systemd service `delo-bot`
- **SSH:** `ssh root@176.57.214.150` (доступ настроен)
- **Server path:** `/opt/delo-bot`
- Статические файлы раздаются FastAPI напрямую (без nginx)

## CI

- `.github/workflows/ci.yml` — тесты на каждый push/PR в main/develop
- Python 3.12, pytest с coverage, ruff linting (optional)

## Git

- GitHub: https://github.com/utkabotron/Delo-Bot
- Коммиты от pavelbrick@gmail.com
