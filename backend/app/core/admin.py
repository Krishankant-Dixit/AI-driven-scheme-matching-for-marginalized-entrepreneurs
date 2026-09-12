from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role", "USER") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return user