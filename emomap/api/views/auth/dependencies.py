from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional, Annotated

from emomap.controllers.auth import AuthController
from emomap.dependencies import AuthControllerDep
from emomap.infrastructure.db.models.users import UserDB


async def get_current_user(
    session_id: Optional[str] = Cookie(None, alias="session_id"),
    auth_controller: AuthController = Depends(AuthControllerDep)
) -> UserDB:
    """
    Dependency to get the current authenticated user from session cookie
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = await auth_controller.validate_session(session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return user 