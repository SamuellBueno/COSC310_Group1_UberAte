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
    No restaurant_id: it comes from the URL"""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = ""
    category: str = Field(min_length=1)
    price: float = Field(gt=0)
    available: bool = True

class MenuItemUpdate(BaseModel):
    """What a client may change on a menu item. every field is optional;
    only the fields that are sent get changed. No restaurant_id so a dish
    can never be moved to another restaurant"""
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, gt=0)
    available: bool | None = None