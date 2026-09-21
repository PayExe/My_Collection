from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.security import create_access_token
from api.dependencies.auth import get_current_user
from api.dependencies.database import get_session
from api.models.user import User
from api.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserPublic
from api.services.auth_service import (
    EmailAlreadyUsedError,
    authenticate_user,
    create_user,
)


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
) -> UserPublic:
    try:
        user = await create_user(session, payload.email, payload.password)
    except EmailAlreadyUsedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email déjà utilisé",
        ) from None

    return UserPublic.model_validate(user)


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
    user = await authenticate_user(session, payload.email, payload.password)
    if user is None:
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
async def get_me(current_user: CurrentUserDependency) -> UserPublic:
    return UserPublic.model_validate(current_user)
