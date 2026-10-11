from sqlalchemy import select

from api.db.database import create_db_and_tables, session_factory
from api.models.game import Game


STEAM_COVER_URL = "https://cdn.cloudflare.steamstatic.com/steam/apps/{}/library_600x900_2x.jpg"
IGDB_COVER_URL = "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/{}.jpg"


def cover_url(cover: int | str) -> str:
    if isinstance(cover, int):
        return STEAM_COVER_URL.format(cover)
    return IGDB_COVER_URL.format(cover)


GAME_SEED: list[dict[str, str | int]] = [
    {
        "titre": title,
        "categorie": category,
        "description": description,
        "image_url": cover_url(cover),
        "annee": year,
        "studio": studio,
        "plateforme": platform,
    }
    for title, category, year, studio, platform, cover, description in [
        ("The Legend of Zelda: Breath of the Wild", "Aventure", 2017, "Nintendo", "Switch, Wii U", "co3p2d",
         "Link se réveille après cent ans de sommeil et explore librement un royaume d'Hyrule en ruines."),
        ("Super Mario Odyssey", "Aventure", 2017, "Nintendo", "Switch", "co1mxf",
         "Mario parcourt des royaumes variés avec Cappy, sa casquette vivante, pour sauver Peach des griffes de Bowser."),
        ("Mario Kart 8 Deluxe", "Course", 2017, "Nintendo", "Switch", "co213p",
         "Des courses déjantées avec les personnages de l'univers Nintendo, objets et circuits antigravité compris."),
        ("Sonic & Sega All-Stars Racing", "Course", 2010, "Sumo Digital", "PC, PS3, Xbox 360, Wii", "co4o3n",
         "Sonic, Tails, AiAi et d'autres stars de SEGA s'affrontent dans des courses de kart pleines d'objets et de raccourcis."),
        ("PaRappa the Rapper 2", "Rythme", 2001, "NanaOn-Sha", "PS2", "co42bg",
         "Le chien PaRappa enchaîne les battles de rap en suivant le rythme pour sauver sa ville transformée en nouilles."),
        ("Silent Hill 2", "Aventure", 2001, "Konami", "PS2, Xbox, PC", "co2vyg",
         "James Sunderland revient à Silent Hill après avoir reçu une lettre de sa femme, morte depuis trois ans."),
        ("Animal Crossing: New Horizons", "Simulation", 2020, "Nintendo", "Switch", "co3wls",
         "S'installer sur une île déserte et l'aménager à son rythme, entouré de voisins animaux."),
        ("Super Smash Bros. Ultimate", "Action", 2018, "Sora Ltd. / Bandai Namco", "Switch", "co2255",
         "Un jeu de combat qui réunit tous les combattants de la série et des invités venus d'autres licences."),
        ("Pokémon Écarlate", "RPG", 2022, "Game Freak", "Switch", "co5sfi",
         "Une aventure en monde ouvert dans la région de Paldea, à la recherche de nouveaux Pokémon à capturer."),
        ("The Legend of Zelda: Tears of the Kingdom", "Aventure", 2023, "Nintendo", "Switch", "co5vmg",
         "Link explore Hyrule, ses îles célestes et ses profondeurs en assemblant ses propres machines."),
        ("Elden Ring", "RPG", 2022, "FromSoftware", "PC, PS5, Xbox Series", 1245620,
         "Un monde ouvert dark fantasy imaginé par FromSoftware et George R. R. Martin, à explorer librement."),
        ("Minecraft", "Simulation", 2011, "Mojang Studios", "PC, Switch, PS4, Xbox One, mobile", "co8fu7",
         "Un monde fait de blocs à explorer, miner et construire, en mode survie ou en mode créatif."),
        ("Red Dead Redemption 2", "Aventure", 2018, "Rockstar Games", "PC, PS4, Xbox One", 1174180,
         "Arthur Morgan et la bande de Dutch van der Linde tentent de survivre à la fin du Far West."),
        ("The Witcher 3: Wild Hunt", "RPG", 2015, "CD Projekt Red", "PC, PS5, Xbox Series, Switch", 292030,
         "Geralt de Riv part à la recherche de Ciri dans un vaste monde ouvert ravagé par la guerre."),
        ("Bloodborne", "Action", 2015, "FromSoftware", "PS4", "cob99l",
         "Un chasseur arpente la ville gothique de Yharnam, rongée par un mal qui transforme ses habitants en bêtes."),
        ("Metroid Dread", "Action", 2021, "MercurySteam", "Switch", "coba9g",
         "Samus Aran explore la planète ZDR, traquée par des robots E.M.M.I. presque invincibles."),
        ("Splatoon 3", "Action", 2022, "Nintendo", "Switch", "co59x3",
         "Des matchs en équipe où l'on recouvre l'arène d'encre pour l'emporter, dans une ambiance très colorée."),
        ("Super Mario Bros. Wonder", "Action", 2023, "Nintendo", "Switch", "co6nnl",
         "Un Mario en 2D plein de surprises, où les fleurs prodiges transforment complètement les niveaux."),
        ("Hades", "Action", 2020, "Supergiant Games", "PC, Switch, PS5, Xbox Series", 1145360,
         "Zagreus tente de s'échapper des Enfers grecs dans un roguelike rapide porté par une narration soignée."),
        ("Hollow Knight", "Action", 2017, "Team Cherry", "PC, Switch, PS4, Xbox One", 367520,
         "Un petit chevalier explore le royaume souterrain d'Hallownest dans un metroidvania dessiné à la main."),
        ("The Last of Us Part I", "Aventure", 2022, "Naughty Dog", "PC, PS5", 1888930,
         "Joel et Ellie traversent des États-Unis ravagés par une pandémie, dans un récit de survie poignant."),
        ("Ghost of Tsushima", "Aventure", 2020, "Sucker Punch Productions", "PC, PS4, PS5", 2215430,
         "Le samouraï Jin Sakai défend l'île de Tsushima contre l'invasion mongole de 1274."),
        ("Baldur's Gate 3", "RPG", 2023, "Larian Studios", "PC, PS5, Xbox Series", 1086940,
         "Un RPG tactique au tour par tour dans l'univers de Donjons et Dragons, où chaque choix compte."),
        ("Final Fantasy VII Remake", "RPG", 2020, "Square Enix", "PC, PS4, PS5", 1462040,
         "Cloud et le groupe Avalanche se dressent contre la Shinra dans la cité de Midgar, avec des combats en temps réel."),
        ("Persona 5 Royal", "RPG", 2019, "Atlus", "PC, PS5, Switch, Xbox Series", 1687950,
         "Des lycéens de Tokyo mènent une double vie de voleurs fantômes pour changer le cœur des adultes corrompus."),
        ("Gran Turismo 7", "Course", 2022, "Polyphony Digital", "PS4, PS5", "co2g84",
         "Une simulation automobile qui célèbre la culture de la voiture, avec plus de 400 modèles à piloter."),
        ("Forza Horizon 5", "Course", 2021, "Playground Games", "PC, Xbox Series, PS5", 1551360,
         "Un festival automobile en monde ouvert à travers les paysages du Mexique."),
        ("F1 23", "Course", 2023, "Codemasters", "PC, PS5, Xbox Series", 2108330,
         "La saison officielle de Formule 1, avec un mode histoire et la gestion de sa propre écurie."),
        ("Crash Team Racing Nitro-Fueled", "Course", 2019, "Beenox", "PS4, Xbox One, Switch", "co2wvy",
         "Le remake du jeu de kart culte de Crash Bandicoot, avec ses circuits et ses personnages remis au goût du jour."),
        ("Need for Speed Heat", "Course", 2019, "Ghost Games", "PC, PS4, Xbox One", 1222680,
         "Des courses officielles le jour et des courses illégales la nuit dans les rues de Palm City."),
        ("Les Sims 4", "Simulation", 2014, "Maxis", "PC, PS4, Xbox One", 1222670,
         "Créer des personnages, construire leur maison et diriger leur vie au quotidien."),
        ("Stardew Valley", "Simulation", 2016, "ConcernedApe", "PC, Switch, PS4, Xbox One", 413150,
         "Reprendre la ferme de son grand-père, cultiver, pêcher et se lier avec les habitants du village."),
        ("Microsoft Flight Simulator", "Simulation", 2020, "Asobo Studio", "PC, Xbox Series", 1250410,
         "Piloter des avions au-dessus de la planète entière, reconstituée à partir de données satellites."),
        ("Cities: Skylines", "Gestion", 2015, "Colossal Order", "PC, PS4, Xbox One, Switch", 255710,
         "Construire et gérer une ville moderne : routes, services publics, budget et circulation."),
        ("Civilization VI", "Gestion", 2016, "Firaxis Games", "PC, PS4, Xbox One, Switch", 289070,
         "Bâtir un empire capable de traverser les âges, de l'Antiquité jusqu'à l'ère spatiale."),
        ("Planet Coaster", "Gestion", 2016, "Frontier Developments", "PC, PS4, Xbox One", 493340,
         "Concevoir son parc d'attractions, des montagnes russes jusqu'à la satisfaction des visiteurs."),
        ("Two Point Hospital", "Gestion", 2018, "Two Point Studios", "PC, PS4, Xbox One, Switch", 535930,
         "Gérer un hôpital rempli de maladies farfelues, avec beaucoup d'humour."),
        ("RimWorld", "Gestion", 2018, "Ludeon Studios", "PC", 294100,
         "Faire survivre une colonie sur une planète lointaine, guidée par un narrateur imprévisible."),
        ("Factorio", "Gestion", 2020, "Wube Software", "PC, Switch", 427520,
         "Bâtir et automatiser une usine géante sur une planète hostile."),
        ("Frostpunk", "Gestion", 2018, "11 bit studios", "PC, PS4, Xbox One", 323190,
         "Diriger la dernière ville de l'humanité dans un monde gelé, en faisant des choix moraux difficiles."),
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
