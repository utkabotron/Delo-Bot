from pydantic import BaseModel
from decimal import Decimal


class CostBreakdownDTO(BaseModel):
    materials: Decimal = Decimal("0")
    metal: Decimal = Decimal("0")
    powder: Decimal = Decimal("0")
    cnc: Decimal = Decimal("0")
    carpentry: Decimal = Decimal("0")
    painting: Decimal = Decimal("0")
    upholstery: Decimal = Decimal("0")
    components: Decimal = Decimal("0")
    box: Decimal = Decimal("0")
    logistics: Decimal = Decimal("0")
    assembly: Decimal = Decimal("0")
    other: Decimal = Decimal("0")


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
    cost_breakdown: CostBreakdownDTO

    class Config:
        from_attributes = True
