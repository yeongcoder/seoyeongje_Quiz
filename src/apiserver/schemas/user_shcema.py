from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    is_admin: bool

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str
    is_admin: bool
    created_at: str
    updated_at: str

