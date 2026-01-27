from pydantic import BaseModel
from decimal import Decimal


class CatalogProductDTO(BaseModel):
    id: int
    name: str
    product_type: str
    base_price: Decimal
    cost_price: Decimal

    class Config:
        from_attributes = True


class CatalogProductGroupedDTO(BaseModel):
    id: int
    name: str
    base_name: str
    product_type: str
    base_price: Decimal
    cost_price: Decimal

    class Config:
        from_attributes = True
