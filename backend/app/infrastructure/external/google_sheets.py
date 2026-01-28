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
    # C: Название, D: Тип, E-P: компоненты себестоимости, Q: Себестоимость, R: База (цена)
    SHEET_NAME = "Справочник Изделий"
    RANGE = "A2:R"  # Пропускаем заголовок

    # Индексы колонок (0-based)
    COL_NAME = 2       # C
    COL_TYPE = 3       # D
    # Cost components (E-P)
    COL_MATERIALS = 4   # E - Материалы
    COL_METAL = 5       # F - Металл каркас
    COL_POWDER = 6      # G - Порошок
    COL_CNC = 7         # H - ЧПУ
    COL_CARPENTRY = 8   # I - Столярка
    COL_PAINTING = 9    # J - Малярка
    COL_UPHOLSTERY = 10 # K - Обивка
    COL_COMPONENTS = 11 # L - Комп.
    COL_BOX = 12        # M - Коробка
    COL_LOGISTICS = 13  # N - Логистика
    COL_ASSEMBLY = 14   # O - Сборка
    COL_OTHER = 15      # P - Прочее
    COL_COST = 16       # Q - Себестоимость
    COL_BASE = 17       # R - База (цена продажи)

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

                # Cost components
                cost_materials = self._parse_price(row[self.COL_MATERIALS] if len(row) > self.COL_MATERIALS else "")
                cost_metal = self._parse_price(row[self.COL_METAL] if len(row) > self.COL_METAL else "")
                cost_powder = self._parse_price(row[self.COL_POWDER] if len(row) > self.COL_POWDER else "")
                cost_cnc = self._parse_price(row[self.COL_CNC] if len(row) > self.COL_CNC else "")
                cost_carpentry = self._parse_price(row[self.COL_CARPENTRY] if len(row) > self.COL_CARPENTRY else "")
                cost_painting = self._parse_price(row[self.COL_PAINTING] if len(row) > self.COL_PAINTING else "")
                cost_upholstery = self._parse_price(row[self.COL_UPHOLSTERY] if len(row) > self.COL_UPHOLSTERY else "")
                cost_components = self._parse_price(row[self.COL_COMPONENTS] if len(row) > self.COL_COMPONENTS else "")
                cost_box = self._parse_price(row[self.COL_BOX] if len(row) > self.COL_BOX else "")
                cost_logistics = self._parse_price(row[self.COL_LOGISTICS] if len(row) > self.COL_LOGISTICS else "")
                cost_assembly = self._parse_price(row[self.COL_ASSEMBLY] if len(row) > self.COL_ASSEMBLY else "")
                cost_other = self._parse_price(row[self.COL_OTHER] if len(row) > self.COL_OTHER else "")

                # Формируем полное название: "Название Тип" (например "СОК Стул")
                full_name = f"{name} {product_type}".strip() if product_type else name

                product = CatalogProduct(
                    name=full_name,
                    product_type=product_type,
                    base_price=base_price,
                    cost_price=cost_price,
                    cost_materials=cost_materials,
                    cost_metal=cost_metal,
                    cost_powder=cost_powder,
                    cost_cnc=cost_cnc,
                    cost_carpentry=cost_carpentry,
                    cost_painting=cost_painting,
                    cost_upholstery=cost_upholstery,
                    cost_components=cost_components,
                    cost_box=cost_box,
                    cost_logistics=cost_logistics,
                    cost_assembly=cost_assembly,
                    cost_other=cost_other,
                )
                products.append(product)

            logger.info(f"Successfully fetched {len(products)} products from Google Sheets")
            return products
        except Exception as e:
            logger.error(f"Failed to fetch catalog from Google Sheets: {e}", exc_info=True)
            raise ExternalServiceException(f"Failed to fetch catalog: {str(e)}")
