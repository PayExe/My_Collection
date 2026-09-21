from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        unique=True,
        index=True,
        min_length=3,
        max_length=254,
    )
    hashed_password: str = Field(max_length=255)
