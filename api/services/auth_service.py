from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.security import hash_password, verify_password
from api.models.user import User


class EmailAlreadyUsedError(Exception):
    """Raised when an account already exists for an email address."""


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def find_user_by_email(session: AsyncSession, email: str) -> User | None:
    normalized_email = normalize_email(email)
    result = await session.exec(
        select(User).where(User.email == normalized_email)
    )
    return result.one_or_none()


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    if await find_user_by_email(session, normalized_email) is not None:
        raise EmailAlreadyUsedError

    user = User(
        email=normalized_email,
        hashed_password=hash_password(password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyUsedError from None

    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await find_user_by_email(session, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
