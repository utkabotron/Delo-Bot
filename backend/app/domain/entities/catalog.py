from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class CatalogProduct:
    id: Optional[int] = None
    name: str = ""
    product_type: str = ""
    base_price: Decimal = Decimal("0")
    cost_price: Decimal = Decimal("0")
