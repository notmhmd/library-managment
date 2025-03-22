from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateBook(BaseModel):
    title: str
    author: str
    category: Optional[str]
    isbn: str
    available_copies: int

class BorrowBook(BaseModel):
    id: int
    book_id: int
    returned_at: Optional[datetime]
    status: str