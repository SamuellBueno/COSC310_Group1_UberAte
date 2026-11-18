from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

Money = Annotated[Decimal, PlainSerializer(lambda v: float(v), return_type=float)]


class CartLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menu_item_id: str = Field(min_length=1)
    quantity: int = Field(ge=1, le=20)


class Cart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    restaurant_id: str | None = None
    items: list[CartLine] = Field(default_factory=list)


class CartLineView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menu_item_id: str
    name: str
    unit_price: Money
    quantity: int
    line_total: Money


class CartView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    customer_id: str
    restaurant_id: str | None
    items: list[CartLineView]
    subtotal: Money
    delivery_fee: Money
    total: Money