from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SessionResponse(BaseModel):
    session_id: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetRequestResponse(BaseModel):
    message: str


class PasswordResetVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class PasswordResetConfirmRequest(BaseModel):
    reset_token: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    new_password: str
