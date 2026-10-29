from fastapi import APIRouter, HTTPException, status

from app.schemas.user import RegisterRequest, UserPublic
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