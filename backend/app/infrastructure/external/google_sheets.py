from decimal import Decimal
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.domain.entities import CatalogProduct
from app.config import get_settings, PROJECT_ROOT
from app.utils.logging import logger
from app.utils.exceptions import ExternalServiceException


class GoogleSheetsService:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # Структура таблицы "Справочник Изделий":
    # C: Название, D: Тип, Q: Себестоимость, R: База (цена)
    SHEET_NAME = "Справочник Изделий"
    RANGE = "A2:R"  # Пропускаем заголовок

    # Индексы колонок (0-based)
    COL_NAME = 2       # C
    COL_TYPE = 3       # D
    COL_COST = 16      # Q - Себестоимость
    COL_BASE = 17      # R - База (цена продажи)

    def __init__(self):
        self.settings = get_settings()
        self._service = None

    def _get_service(self):
        if self._service is None:
            try:
                creds_path = PROJECT_ROOT / "backend" / self.settings.google_credentials_file
                if not creds_path.exists():
                    creds_path = Path(self.settings.google_credentials_file)

                credentials = Credentials.from_service_account_file(
                    str(creds_path), scopes=self.SCOPES
                )
                self._service = build("sheets", "v4", credentials=credentials)
            except Exception as e:
                logger.error(f"Google Sheets authentication error: {e}", exc_info=True)
                raise ExternalServiceException(f"Failed to authenticate with Google Sheets: {str(e)}")
        return self._service

    def _parse_price(self, value: str) -> Decimal:
        """Парсит цену из строки, убирая пробелы и заменяя запятые"""
        if not value:
            return Decimal("0")
        try:
            cleaned = value.replace(" ", "").replace(",", ".").replace("₽", "")
            return Decimal(cleaned)
        except:
            return Decimal("0")

    def fetch_catalog(self) -> list[CatalogProduct]:
        """
        Загружает каталог из Google Sheets.

        Returns:
            List of catalog products

        Raises:
            ExternalServiceException: If Google Sheets API fails
        """
        service = self._get_service()

        try:
            range_name = f"'{self.SHEET_NAME}'!{self.RANGE}"
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.settings.google_sheets_id, range=range_name)
                .execute()
            )
            values = result.get("values", [])

            products = []
            for row in values:
                # Проверяем что есть название
                if len(row) <= self.COL_NAME or not row[self.COL_NAME]:
                    continue

                name = row[self.COL_NAME].strip()
                if not name:
                    continue

                product_type = row[self.COL_TYPE].strip() if len(row) > self.COL_TYPE else ""
                cost_price = self._parse_price(row[self.COL_COST] if len(row) > self.COL_COST else "")
                base_price = self._parse_price(row[self.COL_BASE] if len(row) > self.COL_BASE else "")

                # Формируем полное название: "Название Тип" (например "СОК Стул")
                full_name = f"{name} {product_type}".strip() if product_type else name

                product = CatalogProduct(
                    name=full_name,
                    product_type=product_type,
                    base_price=base_price,
                    cost_price=cost_price,
                )
                products.append(product)

            logger.info(f"Successfully fetched {len(products)} products from Google Sheets")
            return products
        except Exception as e:
            logger.error(f"Failed to fetch catalog from Google Sheets: {e}", exc_info=True)
            raise ExternalServiceException(f"Failed to fetch catalog: {str(e)}")
