from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.infrastructure.external import TelegramValidator


class TelegramMiddleware(BaseHTTPMiddleware):
    """
    Middleware для валидации Telegram initData.
    Можно отключить для разработки.
    """

    def __init__(self, app, enabled: bool = False):
        super().__init__(app)
        self.enabled = enabled
        self.validator = TelegramValidator()

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        # Пропускаем статические файлы и документацию
        if request.url.path.startswith(("/docs", "/openapi.json", "/static")):
            return await call_next(request)

        # Получаем initData из заголовка
        init_data = request.headers.get("X-Telegram-Init-Data", "")

        if not self.validator.validate_init_data(init_data):
            raise HTTPException(status_code=401, detail="Invalid Telegram initData")

        return await call_next(request)
