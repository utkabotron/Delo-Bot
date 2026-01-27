from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base


class CatalogProductModel(Base):
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    product_type = Column(String, default="")
    base_price = Column(Numeric(10, 2), default=0)
    cost_price = Column(Numeric(10, 2), default=0)
