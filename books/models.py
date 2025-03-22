from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship
from common.models import BaseModel


class Book(BaseModel, table=True):
    title: str
    author: str
    category: Optional[str]
    isbn: str = Field(unique=True)
    available_copies: int = Field(default=1, ge=0)
    borrow_history: List["BorrowHistory"] = Relationship(back_populates="book")



class BorrowHistory(BaseModel, table=True):
    user_id: int  = Field(default=None, foreign_key="user.id")
    book_id: int  = Field(default=None, foreign_key="book.id")
    returned_at: Optional[datetime]
    status: str = Field(default="borrowed")
    user: Optional["User"] = Relationship(back_populates="borrow_history")
    book: Optional["Book"] = Relationship(back_populates="borrow_history")