import bcrypt


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