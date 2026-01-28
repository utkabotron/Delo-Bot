from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal


@dataclass
class CatalogProduct:
    id: Optional[int] = None
    name: str = ""
    product_type: str = ""
    base_price: Decimal = Decimal("0")
    cost_price: Decimal = Decimal("0")
    # Cost components
    cost_materials: Decimal = Decimal("0")
    cost_metal: Decimal = Decimal("0")
    cost_powder: Decimal = Decimal("0")
    cost_cnc: Decimal = Decimal("0")
    cost_carpentry: Decimal = Decimal("0")
    cost_painting: Decimal = Decimal("0")
    cost_upholstery: Decimal = Decimal("0")
    cost_components: Decimal = Decimal("0")
    cost_box: Decimal = Decimal("0")
    cost_logistics: Decimal = Decimal("0")
    cost_assembly: Decimal = Decimal("0")
    cost_other: Decimal = Decimal("0")
