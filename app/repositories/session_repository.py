from app.core.security import *
from app.repositories import json_storage
from app.schemas.session import *

FILENAME = "sessions.json"


def add(user_id: str) -> Session:
    """save a new sign in for this user"""
    records = json_storage.read_list(FILENAME)
    session = Session(
        session_id=new_session_id(),
        user_id=user_id,
        #expiry time comes from security.py
        expires_at=session_expiry(),
    )
    records.append(session.model_dump())
    json_storage.write_list(FILENAME, records)
    return session


def get(session_id: str) -> Session | None:
    """returns the session with this id, or None if there isn't one"""
    for record in json_storage.read_list(FILENAME):
        if record["session_id"] == session_id:
            return Session.model_validate(record)
    return None


def delete(session_id: str) -> None:
    """sign out: remove the session with this id"""
    records = json_storage.read_list(FILENAME)
    #for json we rewrite the whole file
    kept = [record for record in records if record["session_id"] != session_id]
    json_storage.write_list(FILENAME, kept)