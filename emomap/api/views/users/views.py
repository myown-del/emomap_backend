from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from typing import Optional

from emomap.controllers.users import UserController
from emomap.controllers.auth import AuthController
from emomap.dependencies import UserControllerDep, AuthControllerDep
from .schemas import UserResponse, ProfileUpdateRequest


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/profile", response_model=UserResponse)
async def get_current_user_profile(
    session_id: Optional[str] = Cookie(None, alias="session_id"),
    auth_controller: AuthController = Depends(AuthControllerDep)
):
    """Get the full profile of the currently logged in user"""
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


@router.put("/me/profile", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: ProfileUpdateRequest,
    session_id: Optional[str] = Cookie(None, alias="session_id"),
    auth_controller: AuthController = Depends(AuthControllerDep),
    user_controller: UserController = Depends(UserControllerDep)
):
    """Update the profile of the currently logged in user"""
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
    
    updated_user = await user_controller.update_user(
        user_id=user.id,
        name=profile_data.name
    )
    return updated_user
