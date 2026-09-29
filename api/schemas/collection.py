from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.game import ItemPublic


Statut = Literal["a_decouvrir", "en_cours", "termine"] # crée un type qui accèpte seulement 3 valeurs


class CollectionCreate(BaseModel):
    """Données nécessaires pour ajouter un jeu à une collection."""

    item_id: int = Field(gt=0)
    statut: Statut
    note: int = Field(ge=1, le=5)
    commentaire: str | None = Field(
        default=None,
        max_length=1000,
    )


class CollectionUpdate(BaseModel):
    """Données facultatives pour modifier une entrée."""

    statut: Statut | None = None
    note: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    commentaire: str | None = Field(
        default=None,
        max_length=1000,
    )


class CollectionEntryPublic(BaseModel):
    """Format d'une entrée de collection dans une réponse API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    statut: Statut
    note: int
    commentaire: str | None
    date_ajout: datetime
    item: ItemPublic


class CollectionStats(BaseModel):
    """Statistiques de la collection d'un utilisateur."""

    total: int
    par_statut: dict[Statut, int]
    note_moyenne: float