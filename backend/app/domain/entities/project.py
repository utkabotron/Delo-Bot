from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal


@dataclass
class ProjectItem:
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    item_type: str = ""
    base_price: Decimal = Decimal("0")
    cost_price: Decimal = Decimal("0")
    quantity: int = 1

    @property
    def subtotal(self) -> Decimal:
        return self.base_price * self.quantity

    @property
    def total_cost(self) -> Decimal:
        return self.cost_price * self.quantity


@dataclass
class Project:
    id: Optional[int] = None
    name: str = ""
    client: str = ""
    global_discount: Decimal = Decimal("0")
    global_tax: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[ProjectItem] = field(default_factory=list)
    notes: str = ""
    is_archived: bool = False

    @property
    def subtotal(self) -> Decimal:
        """Сумма base_price × quantity всех позиций"""
        return sum((item.subtotal for item in self.items), Decimal("0"))

    @property
    def revenue(self) -> Decimal:
        """Subtotal с учётом скидки и налога (оба вычитаются)"""
        discount_multiplier = Decimal("1") - self.global_discount / Decimal("100")
        tax_multiplier = Decimal("1") - self.global_tax / Decimal("100")
        return self.subtotal * discount_multiplier * tax_multiplier

    @property
    def total_cost(self) -> Decimal:
        """Сумма cost_price × quantity всех позиций"""
        return sum((item.total_cost for item in self.items), Decimal("0"))

    @property
    def profit(self) -> Decimal:
        """Revenue - Cost"""
        return self.revenue - self.total_cost

    @property
    def margin(self) -> Decimal:
        """Profit / Revenue × 100%"""
        if self.revenue == 0:
            return Decimal("0")
        return (self.profit / self.revenue) * Decimal("100")
