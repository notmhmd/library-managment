from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request

from common.logging import logging
from users.auth import get_librarian_user, get_current_active_user
from users.models import User
from . import repository
from common.persistance import SessionDep
from .dto import CreateBook, BorrowBook, SearchBook
from .models import Book
from fastapi_cache.decorator import cache


router = APIRouter(prefix="/books", tags=["Books"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=Book)
def add_book(book: CreateBook, session: SessionDep, _: Annotated[User, Depends(get_librarian_user)]):
    try:
        logger.info(f"Adding book: {book.title} by {book.author}")
        return repository.add_book(session, book)
    except Exception as e:
        logger.error(f"Error while adding book {book.title}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error while adding book") from e

@router.get("/", response_model=List[Book])
def get_books(session: SessionDep, _: Annotated[User, Depends(get_current_active_user)], params: SearchBook = Depends()):
    logger.info(f"Fetching books with filter: {params}")
    return repository.get_books(session, params)

@router.get("/{book_id}", response_model=Book)
@cache(namespace="books")
def get_book(book_id: int, session: SessionDep):
    book = repository.get_book(session, book_id)
    if not book:
        logger.warning(f"Book with ID {book_id} not found")
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.patch("/{book_id}", response_model=Book)
async def update_book(book_id: int, session: SessionDep, book: CreateBook, _: Annotated[User, Depends(get_librarian_user)]):
    try:
        logger.info(f"Updating book ID {book_id} with new data")
        return await repository.update_book(session,book, book_id)
    except HTTPException as e:
        logger.warning(f"Update failed for book ID {book_id}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error while updating book ID {book_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="error while updating book") from e

@router.delete("/{book_id}", response_model=dict)
def delete_book(book_id: int, session: SessionDep, _: Annotated[User, Depends(get_librarian_user)]):
    logger.info(f"Deleting book with ID {book_id}")
    return repository.delete_book(session, book_id)

@router.post("/{book_id}/borrow", response_model=BorrowBook)
def borrow_book( book_id: int, session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        logger.info(f"User {current_user.id} is borrowing book ID {book_id}")
        record = repository.borrow_book(session, current_user.id, book_id)
        if not record:
            logger.warning(f"Book ID {book_id} is not available for borrowing")
            raise HTTPException(status_code=400, detail="Book not available")
        return record
    except HTTPException as e:
        logger.warning(f"Borrow attempt failed: {e.detail}")
        raise e

@router.post("/{borrow_id}/return", response_model=BorrowBook)
def return_book(borrow_id: int, session: SessionDep,  current_user: Annotated[User, Depends(get_current_active_user)]):
    logger.info(f"User {current_user.id} is returning book with borrow ID {borrow_id}")
    record = repository.return_book(session, borrow_id, current_user.id)
    if not record:
        logger.warning(f"Invalid borrow ID {borrow_id} or book already returned")
        raise HTTPException(status_code=400, detail="Invalid borrow ID or already returned")
    return record


@router.get("/user/history", response_model=List[BorrowBook])
def borrow_history(session: SessionDep,  current_user: Annotated[User, Depends(get_current_active_user)]):
    logger.info(f"Fetching borrow history for user {current_user.id}")
    record = repository.borrow_history(session, current_user.id)
    if not record:
        logger.warning(f"No borrow history found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="No borrow history")
    return record
