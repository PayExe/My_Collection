# Ma Collection

Application de gestion d'une collection personnelle de jeux vidéo.

Le projet contient une API FastAPI et une interface React qui communique avec cette API.

## Prérequis

- Python 3.12 ou supérieur
- Node.js et npm

## Installation du backend

Depuis la racine du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r api\requirements.txt
Copy-Item api\.env.example api\.env
```

Remplacer ensuite `SECRET_KEY` dans `api/.env` par une valeur secrète longue. Le fichier `.env` ne doit jamais être commit.

## Base et seed

Le backend utilise SQLite avec SQLAlchemy asynchrone. Le seed crée au moins 40 jeux répartis dans plusieurs catégories et peut être relancé sans créer de doublons.

```powershell
python -m api.seed
```

## Lancer l'API

Depuis la racine :

```powershell
python -m uvicorn api.main:app --reload
```

API : http://127.0.0.1:8000

Documentation interactive : http://127.0.0.1:8000/docs

## Installer et lancer le frontend

Dans un second terminal :

```powershell
cd web
npm install
npm run dev
```

Application : http://localhost:5173

Le frontend utilise `http://127.0.0.1:8000` par défaut. Une autre URL peut être configurée avec `VITE_API_URL`.

## Fonctionnalités

- Inscription et connexion avec JWT.
- Catalogue public avec recherche, catégories et pagination.
- Fiche détaillée d'un jeu.
- Collection personnelle protégée par utilisateur.
- Ajout, modification et suppression d'entrées.
- Filtre et tri de la collection.
- Statistiques personnelles.
- Interface responsive.

## Organisation

```text
api/       backend FastAPI, SQLAlchemy et SQLite
web/       frontend React, TypeScript et Vite
docs/      documentation générale du projet
```

Documentation technique du backend : `api/README.md`.

Documentation du CRUD : `api/docs/crud-fonctionnement.md`.

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

## Fichiers ignorés

Les fichiers suivants ne doivent pas être versionnés :

```text
.env
*.db
.venv/
node_modules/
```
