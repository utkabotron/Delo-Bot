from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import get_settings
from app.database import Base, engine
from app.presentation.api import projects_router, catalog_router
from app.presentation.middleware import TelegramMiddleware, AuthMiddleware

# Импортируем модели для создания таблиц
from app.infrastructure.persistence.models import (
    ProjectModel,
    ProjectItemModel,
    CatalogProductModel,
)

settings = get_settings()

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Deloculator API",
    description="Telegram Mini App для расчёта стоимости заказов",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram validation middleware (отключён по умолчанию)
app.add_middleware(TelegramMiddleware, enabled=False)

# Auth middleware
app.add_middleware(AuthMiddleware)

# API routers
app.include_router(projects_router)
app.include_router(catalog_router)

# Статические файлы frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_path / "index.html"))

    @app.get("/login")
    async def serve_login():
        return FileResponse(str(frontend_path / "login.html"))

    @app.get("/project/{project_id}")
    async def serve_project_page(project_id: int):
        return FileResponse(str(frontend_path / "project.html"))


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
