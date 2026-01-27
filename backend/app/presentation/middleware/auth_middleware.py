from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки пароля приложения."""

    # Пути, которые не требуют аутентификации
    PUBLIC_PATHS = [
        "/login",
        "/static/login.html",
        "/api/health",
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Пропускаем публичные пути и статику
        if self._is_public_path(path):
            return await call_next(request)

        # Проверяем пароль в заголовке
        password = request.headers.get("X-Auth-Password")
        settings = get_settings()

        if password != settings.app_password:
            return JSONResponse(
                status_code=401,
                content={"detail": "Неверный пароль"}
            )

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """Проверяет, является ли путь публичным."""
        # Точное совпадение
        if path in self.PUBLIC_PATHS:
            return True

        # Защищаем только API эндпоинты (кроме /api/health)
        # Все остальное (HTML страницы, статика) - публичное
        if not path.startswith("/api/"):
            return True

        return False
