from sqlmodel import select

from common.persistance import SessionDep
from .auth import get_password_hash
from .dto import UserCreate
from .models import User


def create_user(session: SessionDep, user_data: UserCreate):
    hashed_password = get_password_hash(user_data.password)
    roles = list(set(user_data.roles + ["me"]))
    user = User(
        username=user_data.username,
        email=user_data.email,
        name=user_data.name,
        roles=roles,
        password_hash=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: SessionDep, username: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return None
    return user