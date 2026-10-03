from pydantic import BaseModel, ConfigDict, Field


class MenuItem(BaseModel):
    """A menu item as it is stored and returned by the API."""
    id: str
    restaurant_id: str
    name: str = Field(min_length=1)
    description: str = ""
    category: str = Field(min_length=1)
    price: float = Field(gt=0)
    available: bool = True

class MenuItemCreate(BaseModel):
    """What a client sends to add a menu item.
    No id: the server assigns it.
    No restaurant_id: it comes from the URL (POST /restaurants/{restaurant_id}/menu-items),"""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    category: str = Field(min_length=1)
    price: float = Field(gt=0)
    available: bool = True