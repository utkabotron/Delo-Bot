from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import Base, engine
from app.presentation.api import projects_router, catalog_router, security_router
from app.presentation.middleware import (
    TelegramMiddleware,
    AuthMiddleware,
    CSRFMiddleware,
    SecurityHeadersMiddleware,
)
from app.utils.exceptions import DelocatorException
from app.utils.logging import logger

# Импортируем модели (для Alembic autogenerate)
from app.infrastructure.persistence.models import (
    ProjectModel,
    ProjectItemModel,
    CatalogProductModel,
)

settings = get_settings()

# Validate production settings on startup
config_warnings = settings.validate_production_settings()
if config_warnings:
    for warning in config_warnings:
        logger.warning(warning)
    if settings.environment == "production":
        logger.error("Production environment detected with configuration warnings! Review settings immediately.")

# NOTE: Table creation is now handled by Alembic migrations
# Run `alembic upgrade head` to create/update tables
# For backward compatibility during development, you can uncomment the line below:
# Base.metadata.create_all(bind=engine)

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


# Global exception handlers
@app.exception_handler(DelocatorException)
async def delocator_exception_handler(request: Request, exc: DelocatorException):
    """Handle custom application exceptions."""
    logger.warning(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTP error: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        }
    )
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
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

# CSRF protection (before auth, but with backward compat)
app.add_middleware(CSRFMiddleware)

# Auth middleware
app.add_middleware(AuthMiddleware)

# Security headers (applied to all responses)
app.add_middleware(SecurityHeadersMiddleware)

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
