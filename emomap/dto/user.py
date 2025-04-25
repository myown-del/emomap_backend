from pydantic import BaseModel, EmailStr

class UserDTO(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True