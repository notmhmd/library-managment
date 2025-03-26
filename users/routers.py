from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException, status, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from common.logging import logging
from common.persistance import SessionDep
from . import repository
from .auth import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user
from .dto import UserCreate, UserResponse
from .models import User

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)



@router.post("/", response_model=UserResponse)
def register_user(user: UserCreate, session: SessionDep):
    try:
        logger.info(f"Registering new user: {user.username}")
        new_user = repository.create_user(session, user)
        return UserResponse.model_validate(dict(new_user))
    except Exception as e:
        logger.error(f"Error creating user {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="error creating user",
        )

@router.post("/login/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep) -> Token:
    logger.info(f"User login attempt: {form_data.username}")
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User {user.username} logged in successfully")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.roles}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    logger.info(f"Fetching profile for user: {current_user.username}")
    return current_user