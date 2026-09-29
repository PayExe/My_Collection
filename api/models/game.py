from sqlmodel import Field, SQLModel

class Game(SQLModel, table=True):
    """Jeu disponible dans le catalogue public."""

    id: int | None = Field(default= None, primary_key=True) # clé unique
    titre: str = Field(index=True, max_length=200)
    categorie: str = Field(index=True, max_length=100)
    description: str = Field(max_length=2000)
    image_url: str = Field(max_length=500) # adresse de l'image du jeu
    annee: int
    studio: str = Field(max_length=150)
    plateforme: str = Field(max_length=100)