from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.security import get_subject_from_token
from api.dependencies.database import get_session
from api.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)], session: Annotated[AsyncSession, Depends(get_session)]) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    subject = get_subject_from_token(credentials.credentials)
    if subject is None:
        raise unauthorized

    try:
        user_id = int(subject)
    except ValueError:
        raise unauthorized from None

    result = await session.exec(select(User).where(User.id == user_id))
    user = result.one_or_none()
    if user is None:
        raise unauthorized

    return user
