#
from pydantic import BaseModel, ConfigDict, Field

class Restaurant(BaseModel):
        id: str = Field(min_length=1)
        name: str = Field(min_length=1, max_length=80)
        cuisine: str = Field(min_length=1)
        rating: float | None = Field(default = None, ge=0, le=5) # rating is optional as restaurant may not have rating yet
        address: str
        is_open: bool

class RestaurantCreate(BaseModel):
        model_config = ConfigDict(extra="forbid") # don't allow undefined fields

        name: str = Field(min_length=1, max_length=80)
        cuisine: str = Field(min_length=1)
        address: str
        is_open: bool

class RestaurantUpdate(BaseModel):
        model_config = ConfigDict(extra="forbid") # don't allow undefined fields

        name: str | None = Field(default = None, min_length=1, max_length=80)
        cuisine: str | None = Field(default = None, min_length=1)
        address: str | None  = Field(default=None)
        is_open: bool | None = Field(default=None)

