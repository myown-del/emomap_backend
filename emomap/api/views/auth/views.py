from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from fastapi.responses import JSONResponse
from typing import Optional

from emomap.controllers.auth import AuthController
from emomap.controllers.users import UserController
from emomap.dependencies import AuthControllerDep, UserControllerDep
from .schemas import RegisterRequest, LoginRequest, SessionResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def register_simple(
    request: RegisterRequest,
    auth_controller: AuthController = Depends(AuthControllerDep)
):
    """Simplified registration that returns only the session ID"""
    # User validation would happen in the controller
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


@router.post("/login", response_model=SessionResponse)
async def login_simple(
    request: LoginRequest,
    auth_controller: AuthController = Depends(AuthControllerDep)
):
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
