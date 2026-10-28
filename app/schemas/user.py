from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["customer", "restaurant_owner", "admin"]

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class User(BaseModel):
    """an account as it is stored in users.json
    this is not the model we use to send information back"""
    id: str = Field(min_length=1)
    email: str = Field(pattern=EMAIL_PATTERN)
    password_hash: str = Field(min_length=1)
    role: Role
    name: str = Field(min_length=1, max_length=80)
    phone: str | None = None
    delivery_address: str | None = None
    is_active: bool = True
    created_at: str


class UserPublic(BaseModel):
    """this is the one we send back as it does not have the password"""
    id: str
    email: str
    role: Role
    name: str
    phone: str | None = None
    delivery_address: str | None = None
    is_active: bool


class RegisterRequest(BaseModel):
    """what a new customer sends to sign up
    no role field on purpose, so nobody can sign up as an owner or admin"""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: str = Field(pattern=EMAIL_PATTERN, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    delivery_address: str | None = Field(default=None, min_length=1, max_length=160)