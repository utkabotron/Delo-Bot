import hashlib
import hmac
from urllib.parse import parse_qsl
from app.config import get_settings


class TelegramValidator:
    def __init__(self):
        self.settings = get_settings()

    def validate_init_data(self, init_data: str) -> bool:
        """
        Валидация initData от Telegram Mini App.
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """
        if not self.settings.telegram_bot_token:
            # Если токен не задан, пропускаем валидацию (dev mode)
            return True

        try:
            parsed = dict(parse_qsl(init_data, keep_blank_values=True))
            received_hash = parsed.pop("hash", None)
            if not received_hash:
                return False

            # Сортируем параметры и создаём data-check-string
            data_check_string = "\n".join(
                f"{k}={v}" for k, v in sorted(parsed.items())
            )

            # Создаём secret_key
            secret_key = hmac.new(
                b"WebAppData", self.settings.telegram_bot_token.encode(), hashlib.sha256
            ).digest()

            # Вычисляем hash
            calculated_hash = hmac.new(
                secret_key, data_check_string.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(calculated_hash, received_hash)
        except Exception:
            return False

    def parse_user_data(self, init_data: str) -> dict | None:
        """Извлекает данные пользователя из initData"""
        import json

        try:
            parsed = dict(parse_qsl(init_data, keep_blank_values=True))
            user_str = parsed.get("user")
            if user_str:
                return json.loads(user_str)
            return None
        except Exception:
            return None
