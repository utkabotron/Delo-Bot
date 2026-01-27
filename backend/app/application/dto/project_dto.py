from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class ProjectItemCreateDTO(BaseModel):
    name: str
    item_type: str = ""
    base_price: Decimal = Decimal("0")
    cost_price: Decimal = Decimal("0")
    quantity: int = 1


class ProjectItemUpdateDTO(BaseModel):
    quantity: int = Field(ge=1)


class ProjectItemResponseDTO(BaseModel):
    id: int
    name: str
    item_type: str
    base_price: Decimal
    cost_price: Decimal
    quantity: int
    subtotal: Decimal
    total_cost: Decimal

    class Config:
        from_attributes = True


class ProjectSummaryDTO(BaseModel):
    subtotal: Decimal
    revenue: Decimal
    total_cost: Decimal
    profit: Decimal
    margin: Decimal


class ProjectCreateDTO(BaseModel):
    name: str
    client: str = ""
    global_discount: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    global_tax: Decimal = Field(default=Decimal("0"), ge=0)


class ProjectUpdateDTO(BaseModel):
    name: str | None = None
    client: str | None = None
    global_discount: Decimal | None = Field(default=None, ge=0, le=100)
    global_tax: Decimal | None = Field(default=None, ge=0)


class ProjectResponseDTO(BaseModel):
    id: int
    name: str
    client: str
    global_discount: Decimal
    global_tax: Decimal
    created_at: datetime
    items: list[ProjectItemResponseDTO] = []
    summary: ProjectSummaryDTO

    class Config:
        from_attributes = True
