from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str

    class Config:
        from_attributes = True