from decimal import Decimal
from sqlalchemy.orm import Session
from app.domain.entities import CatalogProduct
from app.domain.repositories import ICatalogRepository
from app.infrastructure.persistence.models import CatalogProductModel


class SQLAlchemyCatalogRepository(ICatalogRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: CatalogProductModel) -> CatalogProduct:
        return CatalogProduct(
            id=model.id,
            name=model.name,
            product_type=model.product_type,
            base_price=Decimal(str(model.base_price)),
            cost_price=Decimal(str(model.cost_price)),
        )

    def search(self, query: str, limit: int = 20) -> list[CatalogProduct]:
        models = (
            self.db.query(CatalogProductModel)
            .filter(CatalogProductModel.name.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_all(self) -> list[CatalogProduct]:
        models = self.db.query(CatalogProductModel).all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> CatalogProduct | None:
        model = (
            self.db.query(CatalogProductModel)
            .filter(CatalogProductModel.id == product_id)
            .first()
        )
        if not model:
            return None
        return self._to_entity(model)

    def sync(self, products: list[CatalogProduct]) -> int:
        # Очищаем текущий каталог и загружаем новый
        self.db.query(CatalogProductModel).delete()

        for product in products:
            model = CatalogProductModel(
                name=product.name,
                product_type=product.product_type,
                base_price=product.base_price,
                cost_price=product.cost_price,
            )
            self.db.add(model)

        self.db.commit()
        return len(products)
