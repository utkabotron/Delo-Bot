from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import Base, engine
from app.presentation.api import projects_router, catalog_router, security_router
from app.presentation.middleware import TelegramMiddleware, AuthMiddleware, CSRFMiddleware

# Импортируем модели для создания таблиц
from app.infrastructure.persistence.models import (
    ProjectModel,
    ProjectItemModel,
    CatalogProductModel,
)

settings = get_settings()

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Rate limiter configuration
# Default: 100 requests per minute for all API endpoints
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Deloculator API",
    description="Telegram Mini App для расчёта стоимости заказов",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# CSRF protection (before auth, but with backward compat)
app.add_middleware(CSRFMiddleware)

# Auth middleware
app.add_middleware(AuthMiddleware)

# API routers
app.include_router(security_router)
app.include_router(projects_router)
app.include_router(catalog_router)

# Статические файлы frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # CSS и JS
    css_path = frontend_path / "css"
    js_path = frontend_path / "js"
    if css_path.exists():
        app.mount("/css", StaticFiles(directory=str(css_path)), name="css")
    if js_path.exists():
        app.mount("/js", StaticFiles(directory=str(js_path)), name="js")

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
