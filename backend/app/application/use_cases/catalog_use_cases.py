from app.domain.entities import CatalogProduct
from app.domain.repositories import ICatalogRepository
from app.application.dto import CatalogProductDTO, CatalogProductGroupedDTO


class CatalogUseCases:
    def __init__(self, repository: ICatalogRepository):
        self.repository = repository

    def _extract_base_name(self, name: str, product_type: str) -> str:
        """Извлекает базовое название из полного имени, убирая тип"""
        if product_type and name.endswith(product_type):
            return name[: -len(product_type)].strip()
        return name

    def search_products(self, query: str, limit: int = 20) -> list[CatalogProductDTO]:
        products = self.repository.search(query, limit)
        return [
            CatalogProductDTO(
                id=p.id,
                name=p.name,
                product_type=p.product_type,
                base_price=p.base_price,
                cost_price=p.cost_price,
            )
            for p in products
        ]

    def get_all_grouped(self) -> list[CatalogProductGroupedDTO]:
        """Возвращает все товары с вычисленным базовым названием"""
        products = self.repository.get_all()
        return [
            CatalogProductGroupedDTO(
                id=p.id,
                name=p.name,
                base_name=self._extract_base_name(p.name, p.product_type),
                product_type=p.product_type,
                base_price=p.base_price,
                cost_price=p.cost_price,
            )
            for p in products
        ]

    def sync_catalog(self, products: list[CatalogProduct]) -> int:
        return self.repository.sync(products)

    def get_product(self, product_id: int) -> CatalogProductDTO | None:
        product = self.repository.get_by_id(product_id)
        if not product:
            return None
        return CatalogProductDTO(
            id=product.id,
            name=product.name,
            product_type=product.product_type,
            base_price=product.base_price,
            cost_price=product.cost_price,
        )
