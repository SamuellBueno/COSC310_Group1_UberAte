#
from pydantic import BaseModel, Field

class Restaurant(BaseModel):
        id: str = Field(min_length=1)
        name: str = Field(min_length=1, max_length=80)
        cuisine: str = Field(min_length=1)
        rating: float = Field(ge=0, le=5)
        address: str
        is_open: bool


