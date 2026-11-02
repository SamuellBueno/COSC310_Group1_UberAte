from fastapi import APIRouter, Depends, HTTPException, status

from app.api.role_checks import get_current_user, get_session_id
from app.schemas.user import LoginRequest, LoginResponse, RegisterRequest, User, UserPublic
from app.services import authentication_service

# every route in this file starts with /auth, and is grouped under "authentication" in /docs
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    description="Creates a customer account. Every new account is a customer, there is no role field.",
    responses={
        409: {"description": "An account with this email already exists"},
        422: {"description": "Bad email, password not 5 to 20 characters, or an unknown field such as role"},
    },
)
def register(payload: RegisterRequest):
    # the service checks the email isn't taken and hashes the password
    try:
        return authentication_service.register(payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.post("/login",
    response_model=LoginResponse,
    summary="Sign in",
    description="Checks the email and password and returns a session_id. "
                "Send it as 'Authorization: Bearer <session_id>' on every request after this.",
    responses={
        401: {"description": "Wrong email or password, or the account is deactivated"},
    },
)
def login(payload: LoginRequest):
    # the service checks the password and starts the session
    try:
        return authentication_service.login(payload)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))


@router.post("/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sign out",
    description="Ends the session of the session_id sent with this request.",
    responses={
        401: {"description": "Not signed in, or the session expired"},
        403: {"description": "The account is deactivated"},
    },
    # get_current_user runs first, so a made up or expired session id gets a 401 instead of being "signed out"
    dependencies=[Depends(get_current_user)],
)
def logout(session_id: str = Depends(get_session_id)):
    # we need the session id itself to know which session to delete
    authentication_service.logout(session_id)


@router.get("/me",
    response_model=UserPublic,
    summary="Who am I",
    description="Returns the signed in account, any role. The frontend uses it to know who is signed in.",
    responses={
        401: {"description": "Not signed in, or the session expired"},
        403: {"description": "The account is deactivated"},
    },
)
def me(user: User = Depends(get_current_user)):
    return authentication_service.to_public(user)