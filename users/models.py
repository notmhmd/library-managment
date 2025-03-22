from typing import  List

from pydantic import Json
from sqlalchemy import JSON, Column
from sqlmodel import Relationship, Field

from books.models import BorrowHistory
from common.models import BaseModel


class User(BaseModel, table=True):
    name: str
    username:str = Field(unique=True)
    password_hash: str
    borrow_history: List["BorrowHistory"] = Relationship(back_populates="user")
    email: str = Field(unique=True)
    roles: List[str] = Field(sa_column=Column(JSON), default=[])