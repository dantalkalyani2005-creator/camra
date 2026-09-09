from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import supabase


security = HTTPBearer()


class CurrentUser:
    def __init__(self, user, token: str):
        self.user = user
        self.token = token

    @property
    def id(self):
        return self.user.id

    @property
    def email(self):
        return self.user.email


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if not response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token"
            )

        return CurrentUser(
            user=response.user,
            token=token
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )