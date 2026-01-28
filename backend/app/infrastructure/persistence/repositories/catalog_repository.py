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
            cost_materials=Decimal(str(model.cost_materials or 0)),
            cost_metal=Decimal(str(model.cost_metal or 0)),
            cost_powder=Decimal(str(model.cost_powder or 0)),
            cost_cnc=Decimal(str(model.cost_cnc or 0)),
            cost_carpentry=Decimal(str(model.cost_carpentry or 0)),
            cost_painting=Decimal(str(model.cost_painting or 0)),
            cost_upholstery=Decimal(str(model.cost_upholstery or 0)),
            cost_components=Decimal(str(model.cost_components or 0)),
            cost_box=Decimal(str(model.cost_box or 0)),
            cost_logistics=Decimal(str(model.cost_logistics or 0)),
            cost_assembly=Decimal(str(model.cost_assembly or 0)),
            cost_other=Decimal(str(model.cost_other or 0)),
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
                'cost_materials': p.cost_materials,
                'cost_metal': p.cost_metal,
                'cost_powder': p.cost_powder,
                'cost_cnc': p.cost_cnc,
                'cost_carpentry': p.cost_carpentry,
                'cost_painting': p.cost_painting,
                'cost_upholstery': p.cost_upholstery,
                'cost_components': p.cost_components,
                'cost_box': p.cost_box,
                'cost_logistics': p.cost_logistics,
                'cost_assembly': p.cost_assembly,
                'cost_other': p.cost_other,
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
                'cost_materials': stmt.excluded.cost_materials,
                'cost_metal': stmt.excluded.cost_metal,
                'cost_powder': stmt.excluded.cost_powder,
                'cost_cnc': stmt.excluded.cost_cnc,
                'cost_carpentry': stmt.excluded.cost_carpentry,
                'cost_painting': stmt.excluded.cost_painting,
                'cost_upholstery': stmt.excluded.cost_upholstery,
                'cost_components': stmt.excluded.cost_components,
                'cost_box': stmt.excluded.cost_box,
                'cost_logistics': stmt.excluded.cost_logistics,
                'cost_assembly': stmt.excluded.cost_assembly,
                'cost_other': stmt.excluded.cost_other,
            }
        )

        self.db.execute(stmt)
        self.db.commit()

        return len(products)
