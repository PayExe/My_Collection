from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base import Base


class Game(Base):
    """Jeu disponible dans le catalogue public."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    categorie: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    studio: Mapped[str] = mapped_column(String(150), nullable=False)
    plateforme: Mapped[str] = mapped_column(String(100), nullable=False)
