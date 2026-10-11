from pydantic import BaseModel, ConfigDict


class ItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titre: str
    categorie: str
    description: str
    image_url: str
    annee: int
    studio: str
    plateforme: str


class PaginatedItems(BaseModel):
    total: int
    page: int
    limit: int
    results: list[ItemPublic]
