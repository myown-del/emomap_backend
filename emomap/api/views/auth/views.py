import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from fastapi.responses import JSONResponse
from typing import Optional

from emomap.controllers.auth import AuthController
from emomap.dependencies import AuthControllerDep
from .schemas import (
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    PasswordResetVerifyRequest,
    RegisterRequest,
    SessionResponse,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("uvicorn.error")


@router.post("/register", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def register_simple(
    request: RegisterRequest,
    auth_controller: AuthController = Depends(AuthControllerDep)
):
    """Simplified registration that returns only the session ID"""
    # User validation would happen in the controller
    try:
        session_id = await auth_controller.register(
            email=request.email,
            password=request.password
        )

        response = JSONResponse(
            content={"session_id": session_id},
            status_code=status.HTTP_201_CREATED
        )

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400
        )

        return response
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@router.post("/login", response_model=SessionResponse)
async def login_simple(
    request: LoginRequest,
    auth_controller: AuthController = Depends(AuthControllerDep)
):
    try:
        session_id = await auth_controller.login(
            email=request.email,
            password=request.password
        )

        response = JSONResponse(
            content={"session_id": session_id}
        )

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400
        )

        return response
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(None, alias="session_id"),
    auth_controller: AuthController = Depends(AuthControllerDep)
):
    if session_id:
        await auth_controller.logout(session_id)
    
    response.delete_cookie(key="session_id")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
)
async def password_reset_request(
    request: PasswordResetRequest,
    auth_controller: AuthController = Depends(AuthControllerDep),
):
    await auth_controller.request_password_reset(request.email)
    return {"message": "If this email exists, the reset code has been sent"}


@router.post(
    "/password-reset/verify",
    response_model=bool,
)
async def password_reset_verify(
    request: PasswordResetVerifyRequest,
    auth_controller: AuthController = Depends(AuthControllerDep),
):
    return await auth_controller.verify_password_reset_code(
        email=request.email,
        code=request.code,
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetRequestResponse,
)
async def password_reset_confirm(
    request: PasswordResetConfirmRequest,
    auth_controller: AuthController = Depends(AuthControllerDep),
):
    try:
        await auth_controller.confirm_password_reset(
            reset_token=request.reset_token,
            new_password=request.new_password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {"message": "Password has been reset successfully"}
