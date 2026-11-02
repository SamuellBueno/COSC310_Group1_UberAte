# small functions that run BEFORE a route, to find out who is calling and if they're allowed
# a route asks for one like this:   def get_cart(user: User = Depends(require_customer)):
# fastapi then runs require_customer first and passes its result in as "user"
# if any of these raises an HTTPException, the route never runs and the client gets that error

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user import User
from app.services import authentication_service

# HTTPBearer is fastapi's ready made reader for the header
#   Authorization: Bearer <session_id>
# that every signed in request sends
bearer_scheme = HTTPBearer(auto_error=False, description="Paste the session_id from POST /auth/login")


def get_session_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    """the session id the browser sent with this request, 401 if it didn't send one"""
    # credentials is what bearer_scheme read from the header, or None if there was no header
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in first")
    # credentials.credentials is the text after "Bearer ", which is our session id
    return credentials.credentials


def get_current_user(session_id: str = Depends(get_session_id)) -> User:
    """who is calling, any role used by routes that need someone signed in but don't care which role (like /auth/me)"""
    # the service does all the checking: finds the session, checks expiry, loads the user, checks it's active
    # this function only turns its answer into the right http error
    try:
        user = authentication_service.get_user_for_session(session_id)
    except ValueError as error: #the error is raised by the service for deactivated accounts
        raise HTTPException(status_code=403, detail=str(error))
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Your session is missing or expired, sign in again",
        )
    return user


def require_customer(user: User = Depends(get_current_user)) -> User:
    """only customers get past this for carts, checkout and the customer's own profile"""
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can do this")
    return user


def require_manager(user: User = Depends(get_current_user)) -> User:
    """only restaurant owners and admins get past this for creating and changing restaurants and menus"""
    if user.role not in ("restaurant_owner", "admin"):
        raise HTTPException(status_code=403, detail="Only restaurant owners and admins can do this")
    return user