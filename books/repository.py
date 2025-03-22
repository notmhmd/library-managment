from datetime import datetime
from typing import Annotated

from fastapi import Query, HTTPException
from fastapi_cache import FastAPICache
from sqlmodel import Session, select
from common.persistance import SessionDep
from .dto import CreateBook
from .models import Book, BorrowHistory


def add_book(session: SessionDep, create_book: CreateBook):
    book = Book(**create_book.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


async def update_book(session: SessionDep, update_data: CreateBook, book_id: int):
    book = session.exec(select(Book).where(Book.id == book_id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = update_data.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    await FastAPICache.get_backend().clear(f"fastapi-cache:gir :{book_id}")

    return book


def delete_book(session: SessionDep, book_id: int):
    book = session.exec(select(Book).where(Book.id == book_id)).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
    return {"message": "Book deleted successfully"}

def get_book(session: SessionDep, book_id: int):
    book = session.exec(select(Book).where(Book.id == book_id)).first()
    if book:
        return book
    return None


def get_books(session: SessionDep, offset: int = 0,limit: Annotated[int, Query(le=100)] = 100,):
    books = session.exec(select(Book).offset(offset).limit(limit)).all()
    return books


def borrow_book(session: SessionDep, user_id: int, book_id: int):
    book = session.exec(select(Book).where(Book.id == book_id)).first()
    print(book.available_copies, "copies")
    if book and book.available_copies > 0:
        book.available_copies -= 1
        borrow_record = BorrowHistory(user_id=user_id, book_id=book_id, status="borrowed")
        session.add(borrow_record)
        session.commit()
        return borrow_record
    return None

def return_book(session: SessionDep, borrow_id: int, user_id: int):
    borrow_record = session.exec(select(BorrowHistory).where(BorrowHistory.id == borrow_id, BorrowHistory.status == "borrowed")).first()
    if borrow_record:
        if borrow_record.user_id != user_id: return None
        borrow_record.status = "returned"
        borrow_record.returned_at = datetime.now()
        book = session.exec(select(Book).where(Book.id == borrow_record.book_id)).first()
        book.available_copies += 1
        session.commit()
        return borrow_record
    return None

def borrow_history(session: SessionDep, user_id: int):
    return session.exec(select(BorrowHistory).where(BorrowHistory.user_id == user_id)).all()