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
- `tg.init()` — expand, disableVerticalSwipes, forceLightTheme, safe area
- `tg.forceLightTheme()` — **принудительно устанавливает светлую тему** (игнорирует системную тему Telegram)
- `tg.hapticFeedback(type)` — вибрация (light, medium, heavy, success, error)
- `tg.showBackButton()` / `tg.hideBackButton()`
- `tg.applySafeArea()` — читает `contentSafeAreaInset` и применяет padding к headers

**Темизация:**
- Приложение **всегда использует светлую тему** (белый фон)
- `tg.applyTheme()` закомментирован — не применяем тему из Telegram
- `tg.forceLightTheme()` переопределяет все CSS переменные на светлые значения
- Темная тема для браузера (`@media prefers-color-scheme: dark`) закомментирована
- Для включения темной темы: раскомментировать `@media` в `custom.css` + убрать `forceLightTheme()` в `telegram.js`

CSS переменные в `custom.css`:
- `--tg-bg-color`, `--tg-text-color`, `--tg-hint-color`, `--tg-border-color` и др.
- Tailwind классы (`.bg-gray-100`, `.text-gray-500`, `.active:bg-gray-50`) переопределены для использования переменных
- Для прозрачности границ использовать `rgba()`, НЕ `opacity` (чтобы не влиять на дочерние элементы)
- Active states для карточек: `.active:bg-gray-50:active`, `.active:bg-gray-100:active`

## Аутентификация и безопасность

- Пароль в заголовке `X-Auth-Password` (по умолчанию: `deloculator2024`)
- Поддержка bcrypt хешей (backward compatible с plain text)
- `login.html` проверяет пароль через защищенный endpoint `/api/projects` (НЕ `/api/health`!)
- `api.js` автоматически обрабатывает 401: очищает localStorage + редирект на `/login`
- Rate limiting: 100 req/min глобально, 5 req/min для /api/catalog/sync
- CSRF токены для мутирующих операций
- Security headers (CSP с `'unsafe-inline'` для Alpine.js)

**Важно:** Веб-версия и Telegram-версия используют один и тот же механизм аутентификации через пароль.

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
- **SSH:** `ssh root@176.57.214.150` или `sshpass -p 'eFSpPMVC#,9q?V' ssh -o StrictHostKeyChecking=no ...`
- **Server path:** `/opt/delo-bot`
- Статические файлы раздаются FastAPI напрямую (без nginx)

**Быстрый деплой:**
```bash
sshpass -p 'eFSpPMVC#,9q?V' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password -o PubkeyAuthentication=no root@176.57.214.150 "cd /opt/delo-bot && git pull origin main && sudo systemctl restart delo-bot && echo '✅ Deployed!'"
```

**Проверка после деплоя:**
```bash
# Проверить commit и статус сервиса
ssh root@176.57.214.150 "cd /opt/delo-bot && git log -1 --oneline && systemctl status delo-bot --no-pager | head -10"

# Логи в реальном времени
ssh root@176.57.214.150 "journalctl -u delo-bot -f"

# Проверить миграции
ssh root@176.57.214.150 "cd /opt/delo-bot/backend && source ../venv/bin/activate && alembic current"
```

**Важно при деплое фронтенда:**
- Telegram Mini App **сильно кеширует** JavaScript/CSS файлы
- Изменения могут не появиться мгновенно у пользователей
- Решение: пользователю нужно полностью закрыть Telegram и открыть заново
- Или подождать 2-3 минуты, пока Telegram сам обновит кеш

## CI

- `.github/workflows/ci.yml` — тесты на каждый push/PR в main/develop
- Python 3.12, pytest с coverage, ruff linting (optional)

## Git

- GitHub: https://github.com/utkabotron/Delo-Bot
- Коммиты от pavelbrick@gmail.com

## Распространённые проблемы и решения

### Темизация

**Проблема:** Telegram WebApp SDK автоматически устанавливает CSS переменные на основе темы пользователя, даже если не вызывать `applyTheme()`.

**Решение:** Использовать `forceLightTheme()` для принудительной установки светлых значений переменных.

**Проблема:** Текст не виден в тёмной теме Telegram.

**Причина:** Hardcoded цвета вместо CSS переменных, или использование `opacity` на родительских элементах.

**Решение:**
- Использовать `var(--tg-text-color)`, `var(--tg-hint-color)` вместо конкретных цветов
- Использовать `rgba()` вместо `opacity` для прозрачности

### Аутентификация

**Проблема:** В браузере (не в Telegram) все данные пустые после входа.

**Причина:** `login.html` проверял пароль через публичный endpoint `/api/health`, который всегда возвращает 200 OK.

**Решение:** Проверять пароль через защищенный endpoint `/api/projects`. При 401 очищать localStorage и редиректить на `/login`.

### Скролл и Layout

**Проблема:** Контент не скроллится или скроллится неправильно.

**Причина:** Неправильная комбинация `overflow-hidden` на разных уровнях вложенности.

**Решение:** Изучить паттерны в секции "Frontend Layout Architecture" — два разных подхода для index.html и project.html.

**Проблема:** Клавиатура на iOS сдвигает summary panel.

**Причина:** Viewport изменяется при появлении клавиатуры.

**Решение:** Использовать `100dvh` (dynamic viewport height) + `disableVerticalSwipes()` в Telegram WebApp.
