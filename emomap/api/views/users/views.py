from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from typing import Optional
from sqlalchemy.exc import IntegrityError

from emomap.controllers.users import UserController
from emomap.controllers.auth import AuthController
from emomap.dependencies import UserControllerDep, AuthControllerDep
from .schemas import UserResponse, ProfileUpdateRequest


router = APIRouter(prefix="/users", tags=["Users"])

EMAIL_CONFLICT_MESSAGE = "User with this email already exists"


def _is_email_unique_violation(exc: IntegrityError) -> bool:
    msg = str(getattr(exc, "orig", exc)).lower()
    return "email" in msg and ("unique" in msg or "duplicate key" in msg)


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
    
    try:
        updated_user = await user_controller.update_user(
            user_id=user.id,
            name=profile_data.name,
            email=profile_data.email,
            password=profile_data.password,
        )
        return updated_user
    except ValueError as exc:
        if str(exc) == EMAIL_CONFLICT_MESSAGE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EMAIL_CONFLICT_MESSAGE,
            )
        raise
    except IntegrityError as exc:
        if _is_email_unique_violation(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EMAIL_CONFLICT_MESSAGE,
            )
        raise
