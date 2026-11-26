from pydantic import BaseModel, ConfigDict, Field

class OrderItem(BaseModel):
        menu_item_id: str = Field(min_length=1)
        name: str = Field(min_length=1)
        unit_price: float = Field(gt=0)
        quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
        model_config = ConfigDict(extra="forbid") #Don't allow undefined fields

        customer_id: str = Field(min_length=1)
        restaurant_id: str = Field(min_length=1)
        restaurant_name: str = Field(min_length=1)
        delivery_address: str = Field(min_length=1) # copied at checkout, a later profile change must not rewrite it
        items: list[OrderItem] = Field(min_length=1)
        subtotal: float = Field(ge=0)
        delivery_fee: float = Field(ge=0) # saved so the order still adds up if the fee changes later
        total: float = Field(ge=0)

class Order(OrderCreate):
        id: str = Field(min_length=1)
        status: str
        created_at: str #Saved as text

class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_total: float = Field(ge=0)