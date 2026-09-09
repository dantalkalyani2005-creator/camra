from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.supabase import supabase


router = APIRouter(prefix="/dev", tags=["Development"])


@router.post("/login")
def dev_login():
    if not settings.dev_mode:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": settings.dev_email,
            "password": settings.dev_password
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Development account login failed"
            )

        return {
            "message": "Development login successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )