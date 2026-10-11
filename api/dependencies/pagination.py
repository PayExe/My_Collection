from dataclasses import dataclass

from fastapi import Query


@dataclass
class Pagination:
    page: int
    limit: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


async def get_pagination(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=50),
) -> Pagination:
    return Pagination(page=page, limit=limit)
