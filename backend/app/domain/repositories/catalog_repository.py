from abc import ABC, abstractmethod
from app.domain.entities import CatalogProduct


class ICatalogRepository(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 20) -> list[CatalogProduct]:
        pass

    @abstractmethod
    def get_all(self) -> list[CatalogProduct]:
        pass

    @abstractmethod
    def sync(self, products: list[CatalogProduct]) -> int:
        """Синхронизирует каталог, возвращает количество обновлённых записей"""
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> CatalogProduct | None:
        pass
