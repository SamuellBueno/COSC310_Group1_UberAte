from fastapi import APIRouter, Depends
from app.api.role_checks import require_customer
from app.schemas.user import User, UserPublic, ProfileUpdate
from app.services import customer_service

router = APIRouter(prefix="/customers/me", tags=["customers"])

@router.get("", response_model=UserPublic, summary="View my profile")
def get_my_profile(user: User = Depends(require_customer)):
    return customer_service.get_profile(user.id)

@router.patch("", response_model=UserPublic, summary="Update my profile")
def update_my_profile(payload: ProfileUpdate, user: User = Depends(require_customer)):
    return customer_service.update_profile(user.id, payload)