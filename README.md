# Gamefolio - Ma Collection de jeux vidéo

Application web de gestion d'une collection personnelle de jeux vidéo.

Le projet associe une API FastAPI, une base SQLite asynchrone et une interface React + TypeScript.

## Aperçu

Gamefolio permet de :

- créer un compte et se connecter ;
- consulter un catalogue public de jeux ;
- rechercher, filtrer et paginer le catalogue ;
- consulter la fiche détaillée d'un jeu ;
- ajouter des jeux à sa collection personnelle ;
- modifier le statut, la note et le commentaire d'une entrée ;
- supprimer une entrée ;
- consulter ses statistiques personnelles.

## Prérequis

- Git 2.30 ou supérieur
- Python 3.12 ou supérieur
- Node.js 20 ou supérieur avec npm

## Installation

Depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r api\requirements.txt
Copy-Item api\.env.example api\.env
```

Remplacer ensuite `SECRET_KEY` dans `api/.env` par une clé secrète longue. Ce fichier ne doit jamais être commit.

Dans un second terminal :

```powershell
cd web
npm install
```

## Démarrage rapide

### Backend

Depuis la racine du projet :

```powershell
python -m api.seed
python -m uvicorn api.main:app --reload
```

L'API est disponible sur http://127.0.0.1:8000.

La documentation interactive est disponible sur http://127.0.0.1:8000/docs.

### Frontend

Dans un second terminal :

```powershell
cd web
npm run dev
```

L'application est disponible sur http://localhost:5173.

Le frontend utilise `http://127.0.0.1:8000` par défaut. Une autre adresse peut être définie avec `VITE_API_URL` dans `web/.env.local`.

## Démonstration

1. Ouvrir l'application et créer un compte.
2. Se connecter avec les identifiants créés.
3. Parcourir le catalogue et utiliser la recherche ou les catégories.
4. Ouvrir la fiche d'un jeu.
5. Ajouter le jeu à la collection.
6. Modifier son statut, sa note ou son commentaire.
7. Consulter les statistiques.
8. Supprimer l'entrée ou se déconnecter.

## Architecture

```text
Gamefolio/
├── api/       backend FastAPI, SQLAlchemy et SQLite
├── web/       frontend React, TypeScript et Vite
├── docs/      ADR et documentation générale
└── README.md
```

### Backend

```text
api/
├── core/           configuration et sécurité JWT/bcrypt
├── db/             moteur SQLite et sessions SQLAlchemy
├── dependencies/   session et utilisateur courant
├── models/         tables User, Game et CollectionEntry
├── routers/        routes auth, catalogue et collection
├── schemas/        formats JSON et validation
├── services/       logique métier d'authentification
└── seed.py         peuplement du catalogue
```

### Frontend

```text
web/src/
├── components/     composants partagés et protection des routes
├── contexts/       AuthContext et CollectionContext
├── hooks/          hooks personnalisés
├── pages/          écrans de l'application
├── services/       client HTTP et services métier
├── styles/         styles de l'interface
└── types/          types TypeScript du contrat API
```

## API principale

| Méthode | Route | Accès |
|---|---|---|
| `POST` | `/auth/register` | Public |
| `POST` | `/auth/login` | Public |
| `GET` | `/auth/me` | Authentifié |
| `GET` | `/items` | Public |
| `GET` | `/items/{item_id}` | Public |
| `GET` | `/me/collection` | Authentifié |
| `POST` | `/me/collection` | Authentifié |
| `PATCH` | `/me/collection/{entry_id}` | Authentifié |
| `DELETE` | `/me/collection/{entry_id}` | Authentifié |
| `GET` | `/me/stats` | Authentifié |

Les routes protégées utilisent l'en-tête :

```text
Authorization: Bearer <token>
```

## Documentation

- `api/README.md` : fonctionnement et organisation du backend.
- `api/docs/crud-fonctionnement.md` : fonctionnement de la base et du CRUD.
- `web/docs/authentication-front.md` : authentification et routes React protégées.
- `docs/adr/0001-authentification-jwt.md` : décision concernant l'authentification.
- `docs/guide-utilisateur.md` : guide destiné aux utilisateurs.

## Vérifications

Backend :

```powershell
python -m compileall -q api
```

Frontend :

```powershell
cd web
npm run lint
npm run build
```

## Contribution

1. Créer une branche dédiée depuis `main`.
2. Commiter une fonctionnalité ou une correction cohérente.
3. Tester le backend et le frontend.
4. Ouvrir une Pull Request avec le contexte, les changements et la checklist.
5. Faire relire la Pull Request avant intégration dans `main`.

## Limites connues

- Les tests automatisés peuvent encore être développés davantage.
- Le JWT est stocké dans `localStorage`, ce qui doit être expliqué en soutenance.
- Les fichiers SQLite et `.env` restent locaux et ne sont pas versionnés.

## Licence

Ce projet est distribué sous licence MIT. Voir `LICENSE`.
