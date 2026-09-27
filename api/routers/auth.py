from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

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


router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)

token_router = APIRouter(tags=["Authentification"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
    responses={409: {"description": "Email déjà utilisé"}},
)
async def register(payload: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]) -> UserPublic:
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
    responses={401: {"description": "Identifiants invalides"}},
)
async def login(payload: LoginRequest, session: Annotated[AsyncSession, Depends(get_session)]) -> TokenResponse:
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


@token_router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtenir un token OAuth2",
    responses={401: {"description": "Identifiants invalides"}},
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    user = await authenticate_user(session, form_data.username, form_data.password)
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
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserPublic:
    return UserPublic.model_validate(current_user)
