from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.security import create_access_token, hash_password, verify_password
from api.dependencies.auth import get_current_user
from api.dependencies.database import get_session
from api.models.user import User
from api.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserPublic


router = APIRouter(prefix="/auth", tags=["Authentification"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
    responses={409: {"description": "Email déjà utilisé"}},
)
async def register(
    payload: UserCreate,
    session: SessionDependency,
) -> User:
    email = payload.email.strip().lower()
    result = await session.exec(select(User).where(User.email == email))
    if result.one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email déjà utilisé",
        )

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email déjà utilisé",
        ) from None

    await session.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter",
    responses={401: {"description": "..."}},
)
async def login(
    payload: LoginRequest,
    session: SessionDependency,
) -> TokenResponse:
    email = payload.email.strip().lower()
    result = await session.exec(select(User).where(User.email == email))
    user = result.one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Récupérer l'utilisateur connecté",
    responses={401: {"description": "Authentification invalide"}},
)
async def get_me(current_user: CurrentUserDependency) -> User:
    return current_user
