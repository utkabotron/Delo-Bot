from sqlalchemy import Column, Integer, String, Numeric, UniqueConstraint
from app.database import Base


class CatalogProductModel(Base):
    __tablename__ = "product_catalog"
    __table_args__ = (
        UniqueConstraint('name', 'product_type', name='uix_name_type'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    product_type = Column(String, default="")
    base_price = Column(Numeric(10, 2), default=0)
    cost_price = Column(Numeric(10, 2), default=0)
