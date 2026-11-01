from pydantic import BaseModel


class Session(BaseModel):
    # will be a random token generated at sing_in
    session_id: str
    user_id: str
    # when this sign in stops working, saved as text (comes from security.py)
    expires_at: str