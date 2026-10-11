from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.schemas.game import ItemPublic


Statut = Literal["a_decouvrir", "en_cours", "termine"]


class CollectionCreate(BaseModel):
    item_id: int = Field(gt=0)
    statut: Statut
    note: int | None = Field(default=None, ge=1, le=5)
    commentaire: str | None = Field(
        default=None,
        max_length=1000,
    )


class CollectionUpdate(BaseModel):
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

    @field_validator("statut", mode="before")
    @classmethod
    def reject_null_statut(cls, value: object) -> object:
        if value is None:
            raise ValueError("ne peut pas être null")
        return value


class CollectionEntryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    statut: Statut
    note: int | None
    commentaire: str | None
    date_ajout: datetime
    item: ItemPublic

    @field_validator("date_ajout")
    @classmethod
    def set_utc_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class CollectionStats(BaseModel):
    total: int
    par_statut: dict[Statut, int]
    note_moyenne: float | None
