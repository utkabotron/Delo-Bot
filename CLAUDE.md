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

## Git Configuration

- GitHub account: pavelbrick@gmail.com
