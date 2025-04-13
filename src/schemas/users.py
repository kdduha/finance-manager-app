from pydantic import BaseModel, EmailStr, PastDate
from datetime import datetime


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    birth_date: PastDate | None


class UserUpdateRequest(BaseModel):
    username: str | None
    email: EmailStr | None
    birth_date: PastDate | None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    birth_date: PastDate
    created_at: datetime

    class Config:
        from_attributes = True
