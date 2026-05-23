import string

from pydantic import BaseModel, EmailStr
from pydantic import Field, ConfigDict, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: int = Field(default=1, ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    user_id: int
    priority: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr = Field(min_length=1)
    password: str = Field(min_length=1, max_length=64)

    @field_validator('password')
    def strong_password(cls, v: str):
        if len(v) < 8:
            raise ValueError('password must be longer')
        if not any(char.isupper() for char in v):
            raise ValueError("password must contain at least one upper")
        if not any(char.isdigit() for char in v):
            raise ValueError("password must contain at least one digit")
        if not any(char in string.punctuation for char in v):
            raise ValueError("password must contain at least one special symbol")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
