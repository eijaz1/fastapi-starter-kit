from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str

    class Config:
        orm_mode = True

class UserUpdateForgottenPassword(BaseModel):
    new_password: str
    token: str

    class Config:
        orm_mode = True

class UserShow(BaseModel):
    id: str
    email: str
    password: str
    created_at: datetime

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    description: str

    class Config:
        orm_mode = True

class TaskUpdate(BaseModel):
    description: str

    class Config:
        orm_mode = True

class TaskShow(BaseModel):
    id: str
    description: str
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    id: Optional[int] = None

    class Config:
        orm_mode = True