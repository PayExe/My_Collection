from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.security import get_subject_from_token
from api.dependencies.database import get_session
from api.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = get_subject_from_token(token)
    if subject is None:
        raise unauthorized

    try:
        user_id = int(subject)
    except ValueError:
        raise unauthorized from None

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise unauthorized

    return user
