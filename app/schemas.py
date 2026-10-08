from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    department: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "employee"
    employee_id: Optional[int] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    employee_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"