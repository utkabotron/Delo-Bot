from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
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
        """
        Sync catalog using upsert (insert or update) strategy.
        Preserves existing product IDs and only updates changed data.
        """
        if not products:
            return 0

        # Prepare data for bulk upsert
        product_data = [
            {
                'name': p.name,
                'product_type': p.product_type,
                'base_price': p.base_price,
                'cost_price': p.cost_price,
            }
            for p in products
        ]

        # Use SQLite's INSERT OR REPLACE via on_conflict_do_update
        # This preserves IDs when (name, product_type) matches
        stmt = insert(CatalogProductModel).values(product_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['name', 'product_type'],  # Unique constraint columns
            set_={
                'base_price': stmt.excluded.base_price,
                'cost_price': stmt.excluded.cost_price,
            }
        )

        self.db.execute(stmt)
        self.db.commit()

        return len(products)
