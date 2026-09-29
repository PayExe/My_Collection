from pydantic import BaseModel, ConfigDict


class ItemPublic(BaseModel):
    """Format public d'un jeu dans les réponses API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titre: str
    categorie: str
    description: str
    image_url: str
    annee: int
    studio: str
    plateforme: str