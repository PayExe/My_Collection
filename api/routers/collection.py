from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_session
from api.models.collection_entry import CollectionEntry
from api.models.game import Game
from api.models.user import User
from api.schemas.collection import (
    CollectionCreate,
    CollectionEntryPublic,
    CollectionStats,
    CollectionUpdate,
    Statut,
)
from api.schemas.game import ItemPublic


router = APIRouter(
    prefix="/me",
    tags=["Collection"],
)

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]

CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]

STATUS_VALUES: tuple[Statut, ...] = (
    "a_decouvrir",
    "en_cours",
    "termine",
)


def to_public_entry(
    entry: CollectionEntry,
    game: Game,
) -> CollectionEntryPublic:
    return CollectionEntryPublic(
        id=entry.id,
        statut=entry.statut,
        note=entry.note,
        commentaire=entry.commentaire,
        date_ajout=entry.date_ajout,
        item=ItemPublic.model_validate(game),
    )


async def find_owned_entry(
    session: AsyncSession,
    entry_id: int,
    user_id: int,
) -> tuple[CollectionEntry, Game] | None:
    query = (
        select(CollectionEntry, Game)
        .join(Game, CollectionEntry.game_id == Game.id)
        .where(
            CollectionEntry.id == entry_id,
            CollectionEntry.user_id == user_id,
        )
    )
    result = await session.execute(query)
    return result.one_or_none()


@router.get(
    "/collection",
    response_model=list[CollectionEntryPublic],
    summary="Afficher la collection de l'utilisateur connecté",
    responses={401: {"description": "Authentification invalide"}},
)
async def get_collection(
    current_user: CurrentUserDependency,
    session: SessionDependency,
    statut: Statut | None = Query(default=None),
    tri: Literal["date", "note"] | None = Query(default=None),
) -> list[CollectionEntryPublic]:
    query = (
        select(CollectionEntry, Game)
        .join(Game, CollectionEntry.game_id == Game.id)
        .where(CollectionEntry.user_id == current_user.id)
    )

    if statut is not None:
        query = query.where(CollectionEntry.statut == statut)

    if tri == "note":
        query = query.order_by(CollectionEntry.note.desc())
    else:
        query = query.order_by(CollectionEntry.date_ajout.desc())

    result = await session.execute(query)
    return [
        to_public_entry(entry, game)
        for entry, game in result.all()
    ]


@router.post(
    "/collection",
    response_model=CollectionEntryPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un jeu à la collection",
    responses={
        401: {"description": "Authentification invalide"},
        404: {"description": "Jeu introuvable"},
        409: {"description": "Jeu déjà présent dans la collection"},
    },
)
async def add_to_collection(
    payload: CollectionCreate,
    current_user: CurrentUserDependency,
    session: SessionDependency,
) -> CollectionEntryPublic:
    game = await session.get(Game, payload.item_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jeu introuvable",
        )

    duplicate_query = select(CollectionEntry).where(
        CollectionEntry.user_id == current_user.id,
        CollectionEntry.game_id == payload.item_id,
    )
    duplicate = await session.scalar(duplicate_query)
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jeu déjà présent dans la collection",
        )

    entry = CollectionEntry(
        user_id=current_user.id,
        game_id=payload.item_id,
        statut=payload.statut,
        note=payload.note,
        commentaire=payload.commentaire,
    )
    session.add(entry)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jeu déjà présent dans la collection",
        ) from None

    await session.refresh(entry)
    return to_public_entry(entry, game)


@router.patch(
    "/collection/{entry_id}",
    response_model=CollectionEntryPublic,
    summary="Modifier une entrée de collection",
    responses={
        401: {"description": "Authentification invalide"},
        404: {"description": "Entrée introuvable"},
    },
)
async def update_collection_entry(
    entry_id: int,
    payload: CollectionUpdate,
    current_user: CurrentUserDependency,
    session: SessionDependency,
) -> CollectionEntryPublic:
    owned_entry = await find_owned_entry(
        session,
        entry_id,
        current_user.id,
    )
    if owned_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrée introuvable",
        )

    entry, game = owned_entry
    provided_fields = payload.model_fields_set

    if "statut" in provided_fields:
        entry.statut = payload.statut  # type: ignore[assignment]
    if "note" in provided_fields:
        entry.note = payload.note  # type: ignore[assignment]
    if "commentaire" in provided_fields:
        entry.commentaire = payload.commentaire

    await session.commit()
    await session.refresh(entry)
    return to_public_entry(entry, game)


@router.delete(
    "/collection/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une entrée de collection",
    responses={
        401: {"description": "Authentification invalide"},
        404: {"description": "Entrée introuvable"},
    },
)
async def delete_collection_entry(
    entry_id: int,
    current_user: CurrentUserDependency,
    session: SessionDependency,
) -> Response:
    owned_entry = await find_owned_entry(
        session,
        entry_id,
        current_user.id,
    )
    if owned_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrée introuvable",
        )

    entry, _ = owned_entry
    await session.delete(entry)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/stats",
    response_model=CollectionStats,
    summary="Afficher les statistiques de la collection",
    responses={401: {"description": "Authentification invalide"}},
)
async def get_collection_stats(
    current_user: CurrentUserDependency,
    session: SessionDependency,
) -> CollectionStats:
    user_filter = CollectionEntry.user_id == current_user.id
    total_query = select(func.count(CollectionEntry.id)).where(user_filter)
    total = int((await session.scalar(total_query)) or 0)

    status_query = (
        select(CollectionEntry.statut, func.count(CollectionEntry.id))
        .where(user_filter)
        .group_by(CollectionEntry.statut)
    )
    status_rows = (await session.execute(status_query)).all()
    status_counts = {status_value: 0 for status_value in STATUS_VALUES}
    for entry_status, count in status_rows:
        if entry_status in status_counts:
            status_counts[entry_status] = int(count)

    average_query = select(func.avg(CollectionEntry.note)).where(user_filter)
    average = await session.scalar(average_query)

    return CollectionStats(
        total=total,
        par_statut=status_counts,
        note_moyenne=float(average or 0),
    )
