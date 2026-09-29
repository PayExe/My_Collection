from urllib.parse import quote

from sqlalchemy import select

from api.db.database import create_db_and_tables, session_factory
from api.models.game import Game


GAME_SEED: list[dict[str, str | int]] = [
    {
        "titre": f"{title} {suffix}",
        "categorie": category,
        "description": f"{title} {suffix}, une aventure à découvrir dans la collection.",
        "image_url": f"https://placehold.co/640x900/203d5a/ffffff?text={quote(title)}",
        "annee": year,
        "studio": studio,
        "plateforme": platform,
    }
    for title, suffix, category, year, studio, platform in [
        ("Neon Horizon", "Zero", "Action", 2024, "Northstar", "PC"),
        ("Neon Horizon", "Afterlight", "Action", 2025, "Northstar", "PC"),
        ("Wildwood", "Origins", "Aventure", 2022, "Oak Studio", "Switch"),
        ("Wildwood", "The North", "Aventure", 2024, "Oak Studio", "Switch"),
        ("Pixel Odyssey", "Chapter One", "RPG", 2021, "Moonbyte", "PC"),
        ("Pixel Odyssey", "Starlight", "RPG", 2023, "Moonbyte", "PC"),
        ("Turbo Club", "Velocity", "Course", 2025, "Redline", "PS5"),
        ("Turbo Club", "Street League", "Course", 2024, "Redline", "Xbox"),
        ("Moon Colony", "First Light", "Simulation", 2022, "Orbit Works", "PC"),
        ("Moon Colony", "Terraform", "Simulation", 2025, "Orbit Works", "PC"),
        ("Cafe Stories", "Morning Shift", "Gestion", 2023, "Kindred", "Switch"),
        ("Cafe Stories", "Night Owls", "Gestion", 2025, "Kindred", "Switch"),
        ("Iron Vale", "The Foundry", "Action", 2020, "Forge Lab", "PC"),
        ("Iron Vale", "Rebellion", "Action", 2023, "Forge Lab", "PC"),
        ("Sable Coast", "Tides", "Aventure", 2021, "Blue Finch", "PS5"),
        ("Sable Coast", "Low Country", "Aventure", 2024, "Blue Finch", "PS5"),
        ("Starfall", "The Last Signal", "RPG", 2022, "Orbit Works", "PC"),
        ("Starfall", "New Dawn", "RPG", 2025, "Orbit Works", "PC"),
        ("Driftline", "Midnight", "Course", 2021, "Redline", "Xbox"),
        ("Driftline", "Grand Tour", "Course", 2024, "Redline", "Xbox"),
        ("Greenhouse", "Seasons", "Simulation", 2020, "Kindred", "Switch"),
        ("Greenhouse", "Wild Growth", "Simulation", 2023, "Kindred", "Switch"),
        ("Market Street", "Corner Shop", "Gestion", 2022, "Oak Studio", "Switch"),
        ("Market Street", "Night Market", "Gestion", 2024, "Oak Studio", "Switch"),
        ("Blackout", "Protocol", "Action", 2021, "Northstar", "PC"),
        ("Blackout", "Aftermath", "Action", 2025, "Northstar", "PC"),
        ("Hidden Atlas", "The Map Room", "Aventure", 2020, "Blue Finch", "PS5"),
        ("Hidden Atlas", "Lost Routes", "Aventure", 2023, "Blue Finch", "PS5"),
        ("Mythic Isles", "Awakening", "RPG", 2021, "Moonbyte", "PC"),
        ("Mythic Isles", "The Deep", "RPG", 2024, "Moonbyte", "PC"),
        ("Apex Run", "Overtake", "Course", 2022, "Forge Lab", "PS5"),
        ("Apex Run", "Final Lap", "Course", 2025, "Forge Lab", "PS5"),
        ("After Earth", "Shelter", "Simulation", 2021, "Orbit Works", "PC"),
        ("After Earth", "New Soil", "Simulation", 2024, "Orbit Works", "PC"),
        ("Tiny Empire", "First City", "Gestion", 2020, "Kindred", "PC"),
        ("Tiny Empire", "The Trade Route", "Gestion", 2023, "Kindred", "PC"),
        ("Red Sector", "Entry Point", "Action", 2022, "Northstar", "Xbox"),
        ("Red Sector", "Lockdown", "Action", 2024, "Northstar", "Xbox"),
        ("Far North", "Whiteout", "Aventure", 2022, "Blue Finch", "PS5"),
        ("Far North", "The Long Way", "Aventure", 2025, "Blue Finch", "PS5"),
    ]
]


async def seed_catalog() -> None:
    await create_db_and_tables()
    async with session_factory() as session:
        existing_titles = set((await session.scalars(select(Game.titre))).all())
        for game_data in GAME_SEED:
            if game_data["titre"] not in existing_titles:
                session.add(Game(**game_data))
        await session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_catalog())
