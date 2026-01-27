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
- `dashboard()` — управление списком проектов (загрузка, создание, удаление)
- `projectEditor()` — редактирование проекта (метаданные, позиции, поиск по каталогу)
- Все расчёты (subtotal, revenue, profit, margin) происходят реактивно на клиенте

**Редактирование количества (project.html):**
- Клик по числу количества → открывает модальное окно (`showQuantityModal`)
- Модалка использует `setTimeout()` для автофокуса (надёжнее чем `$nextTick`)
- Input автоматически выделяет весь текст (`select()`) → клавиатура появляется сразу
- Кнопки +/- для быстрых изменений, модалка для точного ввода больших чисел

**Важно для Alpine.js:**
- `x-show` НЕ работает надёжно внутри `x-for` — использовать `:class="condition ? 'hidden' : ''"` или `x-if` с `<template>`
- Для доступа к элементам лучше использовать `document.getElementById()` чем `x-ref` (особенно в модалках)
- События: `@blur` надёжнее чем `@change` на мобильных устройствах

## Telegram Mini App

Интеграция через `telegram.js`:
- `tg.init()` — инициализация (expand, theme, safe area)
- `tg.applyTheme()` — автоматическое применение Telegram theme (светлая/тёмная)
- `tg.applySafeArea()` — отступы под системные элементы Telegram
- `tg.hapticFeedback(type)` — вибрация (light/medium/heavy/success/error)
- `tg.showBackButton()` / `tg.hideBackButton()` — кнопка "назад"

Настройка бота в @BotFather:
- `/mybots` → выбрать бота → **Mini Apps** → **Menu Button**
- URL: `https://delo.brdg.tools`

Токен бота хранится в `.env` → `TELEGRAM_BOT_TOKEN`

### Темизация и Accessibility

**CSS Переменные Telegram (`frontend/css/custom.css`):**
- `--tg-bg-color` — основной фон
- `--tg-section-bg-color` — фон карточек/секций
- `--tg-secondary-bg-color` — вторичный фон (badges, disabled fields)
- `--tg-text-color` — основной цвет текста
- `--tg-subtitle-text-color` — цвет подзаголовков (#707070, контраст 4.54:1)
- `--tg-hint-color` — цвет подсказок/hints (#6c757d, контраст 5.74:1)
- `--tg-link-color` / `--tg-button-color` — цвет ссылок и кнопок

**WCAG AA Compliance:**
- Все текстовые цвета соответствуют минимальной контрастности 4.5:1
- Использованы `rgba()` для прозрачности границ (НЕ `opacity` на элементе!)
- Яркие цветные акценты (Apple-style):
  - Прибыль: `#10b981` (ярко-зелёный)
  - Убыток: `#ef4444` (ярко-красный)
  - Скидки/Налоги: `#f97316` (оранжевый)

**Важные CSS правила:**
- Tailwind классы (bg-white, text-gray-*) переопределены для использования Telegram theme
- `.border-*` использует `rgba()` для прозрачности, а НЕ `opacity` (чтобы не влиять на дочерние элементы)
- Цветные акценты (`text-green-600`, `text-red-600`) всегда яркие через `!important`

**Spacing и отступы (project.html):**
- Main content: `p-4` (16px со всех сторон), `pb-60` (240px снизу под fixed panel)
- Между карточками: `space-y-3` (12px) — сбалансировано с общими отступами 16px
- Кнопка "Добавить": `mb-4` (16px снизу) — соответствует основным отступам
- **Принцип:** Основные отступы 16px (p-4, mb-4), между элементами 12px (space-y-3)

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

## Распространённые проблемы и решения

### Проблемы с темизацией

**Проблема:** Текст не виден в тёмной теме Telegram
- **Причина:** Hardcoded цвета вместо CSS переменных Telegram
- **Решение:** Использовать `var(--tg-text-color)`, `var(--tg-hint-color)` и т.д.
- **Файл:** `frontend/css/custom.css`

**Проблема:** "Серая полупрозрачная плашка" или приглушённые цвета
- **Причина:** Использование `opacity` на родительском элементе (наследуется на детей)
- **Решение:** Использовать `rgba()` с альфа-каналом вместо `opacity`
- **Пример:**
  ```css
  /* Плохо - делает весь элемент прозрачным */
  .border-t {
      border-color: #6c757d;
      opacity: 0.35;
  }

  /* Хорошо - прозрачен только цвет границы */
  .border-t {
      border-color: rgba(108, 117, 125, 0.35);
  }
  ```

**Проблема:** Контрастность не соответствует WCAG AA
- **Требования:** Минимум 4.5:1 для обычного текста, 3:1 для крупного (18pt+)
- **Инструменты:** WebAIM Contrast Checker, Chrome DevTools
- **Решение:** Использовать более тёмные оттенки серого (#6c757d вместо #999999)

### Проблемы с Alpine.js

**Проблема:** Элементы не появляются/исчезают при использовании `x-show` внутри `x-for`
- **Причина:** Alpine.js v3 плохо обрабатывает `x-show` в циклах
- **Решение:** Использовать `:class="condition ? 'hidden' : ''"` или `x-if` с `<template>`
- **Пример:** `<button :class="editingItemId === item.id ? 'hidden' : ''">+</button>`

**Проблема:** Input не получает фокус автоматически в модалке
- **Причина:** `$nextTick` не всегда работает с анимациями Alpine.js
- **Решение:** Использовать `setTimeout(() => document.getElementById('id').focus(), 100)`
- **Файл:** `frontend/js/app.js:328-340`

**Проблема:** Клавиатура не появляется на мобильном при открытии модалки
- **Причина:** Нет явного вызова `.focus()` на input
- **Решение:** После открытия модалки вызвать `input.focus()` + `input.select()`

### Проблемы с layout на мобильных

**Проблема:** Summary panel "подпрыгивает" когда появляется клавиатура
- **Причина:** `100vh` включает виртуальную клавиатуру, flex layout пересчитывается
- **Решение:**
  - Body: `height: 100dvh` (dynamic viewport height) с fallback `100vh`
  - Summary panel: `position: fixed; bottom: 0` вместо `flex-shrink-0`
  - Main content: достаточный `padding-bottom` (~240px для панели высотой 200px)
- **Файлы:** `frontend/project.html:12,36,116`

**Проблема:** Контент скрыт под фиксированным summary panel
- **Причина:** Недостаточный `padding-bottom` у main content
- **Решение:** Измерить высоту панели + добавить запас 20-40px. Например: `pb-60` (240px) для панели ~200px
- **Файл:** `frontend/project.html:36`

### Проблемы с deployment

**Проблема:** Изменения не применяются после деплоя
- **Решение:** Проверить что сервис перезапущен: `sudo systemctl status delo-bot`
- **Проверить:** `git log -1` на сервере совпадает с локальным

**Проблема:** CSS не обновляется в браузере
- **Причина:** Кеш браузера
- **Решение:** Hard refresh (Cmd+Shift+R на Mac, Ctrl+Shift+R на Windows)

## Git Configuration

- GitHub: https://github.com/utkabotron/Delo-Bot (public)
- GitHub account: pavelbrick@gmail.com
- **Важно:** Все коммиты должны быть от pavelbrick@gmail.com
