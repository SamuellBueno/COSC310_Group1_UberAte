import bcrypt
from datetime import datetime, timedelta, timezone
import secrets

#how much time sing in lasts
SESSION_DURATION = 6


def hash_password(password: str) -> str:
    """turn a password into a bcrypt hash"""
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored: str) -> bool:
    """true if the password matches the stored hash"""
    password_bytes = password.encode("utf-8")
    try:
        return bcrypt.checkpw(password_bytes, stored.encode("utf-8"))
    except ValueError:
        #if it goes wrong probably was not a password 
        return False


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def session_expiry() -> str:
    # the time a sign in made + duration as text for the json file
    expiry_time = now_utc() + timedelta(hours=SESSION_DURATION)
    return expiry_time.isoformat()


def is_expired(expires_at: str) -> bool:
    # gets the expered time established in json and compares with now
    expiry_time = datetime.fromisoformat(expires_at)
    return expiry_time <= now_utc() # returns true or false


def new_session_id() -> str:
    # a long random 32 bytes str nobody can guess, made fresh at every sign in. serves as session id
    return secrets.token_urlsafe(32)