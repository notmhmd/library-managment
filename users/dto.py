from typing import Optional, List

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    name: str
    password: str
    roles: list[str]

class UserResponse(BaseModel):
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str]