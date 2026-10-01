from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base import Base


class CollectionEntry(Base):
    """Jeu ajouté dans la collection personnelle d'un utilisateur."""

    __tablename__ = "collection_entries"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "game_id",
            name="unique_user_game",
        ),
        CheckConstraint(
            "statut IN ('a_decouvrir', 'en_cours', 'termine')",
            name="valid_collection_status",
        ),
        CheckConstraint(
            "note BETWEEN 1 AND 5",
            name="valid_collection_note",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id"),
        index=True,
        nullable=False,
    )
    statut: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[int] = mapped_column(Integer, nullable=False)
    commentaire: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    date_ajout: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
