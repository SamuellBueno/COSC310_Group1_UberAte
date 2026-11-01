from pydantic import ValidationError

from app.repositories import json_storage
from app.schemas.user import RegisterRequest, User

FILENAME = "users.json"


def list_all() -> list[User]:
    """every account in the file"""
    records = json_storage.read_list(FILENAME)
    try:
        return [User.model_validate(record) for record in records]
    except ValidationError as exc:
        raise ValueError(f"Invalid record or value in {FILENAME}") from exc


def get_by_id(user_id: str) -> User | None:
    """the account with this id, or None"""
    for user in list_all():
        if user.id == user_id:
            return user
    return None


def get_by_email(email: str) -> User | None:
    """the account with this email, capitals don't matter
    emails are stored lowercase so lowering the one we're given is enough"""
    for user in list_all():
        if user.email == email.lower():
            return user
    return None


def add_customer(payload: RegisterRequest, password_hash: str) -> User:
    """save a new customer with the next U id
    the role is always customer here, the hash is made by the service before calling this"""
    records = json_storage.read_list(FILENAME)
    user = User(
        id=json_storage.next_id(records, "U"),
        email=payload.email.lower(),
        password_hash=password_hash,
        role="customer",
        name=payload.name,
        phone=payload.phone,
        delivery_address=payload.delivery_address,
        is_active=True
    )
    records.append(user.model_dump())
    json_storage.write_list(FILENAME, records)
    return user


def update(user_id: str, changes: dict) -> User | None:
    """apply a dict of changes to one account, check the result is still valid, save it
    returns None if there is no account with this id"""
    records = json_storage.read_list(FILENAME)
    for index, record in enumerate(records):
        if record["id"] == user_id:
            updated_record = dict(record)
            updated_record.update(changes)
            user = User.model_validate(updated_record)
            records[index] = user.model_dump()
            json_storage.write_list(FILENAME, records)
            return user
    return None