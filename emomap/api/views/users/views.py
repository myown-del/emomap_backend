from fastapi import APIRouter, Depends, HTTPException, status

from emomap.controllers.users import UserController
from emomap.dependencies import UserControllerDep
from emomap.infrastructure.db.models.users import UserDB
from emomap.schemas.user import UserCreateRequest, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(user_controller: UserController = Depends(UserControllerDep)):
    users = await user_controller.get_all(limit=10)
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreateRequest,
    user_controller: UserController = Depends(UserControllerDep)
):
    existing_user = await user_controller.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )
    
    new_user = await user_controller.create(email=user_in.email, password=user_in.password)
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    user_controller: UserController = Depends(UserControllerDep)
):
    user = await user_controller.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
