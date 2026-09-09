from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router = APIRouter(prefix="/test-auth", tags=["Authentication Test"])


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email
    }