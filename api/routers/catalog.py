from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.database import get_session
from api.models.game import Game
from api.schemas.game import ItemPublic, PaginatedItems


router = APIRouter(tags=["Catalogue"])


@router.get(
    "/items",
    response_model=PaginatedItems,
    summary="Rechercher dans le catalogue",
)
async def list_items(
    session: Annotated[AsyncSession, Depends(get_session)],
    q: str | None = Query(default=None, min_length=2),
    categorie: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=50),
) -> PaginatedItems:
    filters = []
    if q:
        search = f"%{q}%"
        filters.append(or_(Game.titre.ilike(search), Game.description.ilike(search)))
    if categorie:
        filters.append(Game.categorie == categorie)

    count_query = select(func.count()).select_from(Game).where(*filters)
    total = int((await session.scalar(count_query)) or 0)
    games_query = (
        select(Game)
        .where(*filters)
        .order_by(Game.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    games = (await session.scalars(games_query)).all()

    return PaginatedItems(
        total=total,
        page=page,
        limit=limit,
        results=[ItemPublic.model_validate(game) for game in games],
    )


@router.get(
    "/items/categories",
    response_model=list[str],
    summary="Lister les catégories du catalogue",
)
async def list_categories(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[str]:
    categories = await session.scalars(
        select(Game.categorie).distinct().order_by(Game.categorie)
    )
    return list(categories.all())


@router.get(
    "/items/{item_id}",
    response_model=ItemPublic,
    summary="Consulter le détail d'un jeu",
    responses={404: {"description": "Jeu introuvable"}},
)
async def get_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ItemPublic:
    game = await session.get(Game, item_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jeu introuvable",
        )
    return ItemPublic.model_validate(game)
