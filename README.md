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
- consulter ses statistiques personnelles ;
- basculer entre thème sombre et thème clair.

## Démarrage rapide

### Prérequis

- Python 3.12 ou supérieur : vérifier avec `python --version`
- Node.js 20 ou supérieur avec npm : vérifier avec `node --version`
- Git
- Une connexion internet, pour installer les dépendances et afficher les jaquettes des jeux
- Les ports `8000` (API) et `5173` (interface) libres

### 1. Récupérer le projet

```bash
git clone https://github.com/PayExe/My_Collection.git
cd My_Collection
```

### 2. Installer et lancer l'API (terminal 1)

Toutes les commandes se lancent depuis la racine du projet (`My_Collection`), jamais depuis `api/`.

**Windows (PowerShell)**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r api\requirements.txt
Copy-Item api\.env.example api\.env
$key = python -c "import secrets; print(secrets.token_hex(32))"
(Get-Content api\.env) -replace '^SECRET_KEY=.*', "SECRET_KEY=$key" | Set-Content api\.env
python -m api.seed
python -m uvicorn api.main:app --reload
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r api/requirements.txt
cp api/.env.example api/.env
KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$KEY/" api/.env && rm api/.env.bak
python -m api.seed
python -m uvicorn api.main:app --reload
```

Ces commandes :

- créent et activent un environnement virtuel Python (`.venv`) ;
- installent les dépendances de l'API ;
- créent `api/.env` à partir de `api/.env.example`, avec une clé JWT aléatoire (ce fichier n'est jamais versionné) ;
- remplissent le catalogue avec 40 jeux (relancer `python -m api.seed` ne crée pas de doublon) ;
- démarrent l'API sur http://127.0.0.1:8000, avec sa documentation interactive sur http://127.0.0.1:8000/docs.

Laisser ce terminal ouvert.

### 3. Installer et lancer l'interface (terminal 2)

```bash
cd web
npm install
npm run dev
```

Ouvrir http://localhost:5173, créer un compte puis se connecter.

L'interface appelle l'API sur `http://127.0.0.1:8000` par défaut. Une autre adresse peut être définie avec `VITE_API_URL` dans `web/.env.local`. L'interface doit rester sur le port `5173` : c'est la seule origine autorisée par le CORS de l'API.

### Relancer le projet plus tard

L'installation ne se fait qu'une fois. Les fois suivantes, il suffit de rouvrir deux terminaux à la racine du projet.

Terminal 1 (API) :

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --reload
```

Sur macOS / Linux, la première ligne devient `source .venv/bin/activate`.

Terminal 2 (interface) :

```bash
cd web
npm run dev
```

### Dépannage

| Problème | Solution |
|---|---|
| `No module named 'sqlalchemy'` ou `No module named uvicorn` | L'environnement virtuel n'est pas activé dans ce terminal : lancer `.\.venv\Scripts\Activate.ps1` (ou `source .venv/bin/activate`), puis relancer la commande. |
| `Activate.ps1` refusé (« l'exécution de scripts est désactivée sur ce système ») | Lancer `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, puis réessayer. Ce réglage ne concerne que le terminal ouvert. |
| `Python was not found` ou `python` n'est pas reconnu (Windows) | Python n'est pas dans le PATH. Réinstaller Python depuis python.org en cochant « Add python.exe to PATH », puis ouvrir un nouveau terminal. |
| `RuntimeError: SECRET_KEY manquante dans le fichier .env` | Le fichier `api/.env` est absent ou sa clé est vide : refaire les étapes `Copy-Item` (ou `cp`) et `SECRET_KEY` de l'installation. |
| `No module named 'api'` | La commande a été lancée depuis le dossier `api/` : revenir à la racine du projet. |
| `address already in use` au lancement de l'API | Une autre API tourne déjà sur le port 8000 : l'arrêter (Ctrl+C dans son terminal), puis relancer. |
| `Port 5173 is already in use` | Une autre interface Vite tourne déjà : l'arrêter, puis relancer `npm run dev`. |
| Le catalogue est vide | Lancer `python -m api.seed`, environnement virtuel activé. |
| « Impossible de contacter le serveur » ou « Impossible de charger le catalogue » | L'API n'est pas démarrée, ou l'interface n'est pas ouverte sur http://localhost:5173. |
| Repartir d'une base vide | Arrêter l'API (Ctrl+C), supprimer `ma_collection.db` à la racine, puis relancer `python -m api.seed`. Les comptes créés sont perdus. |

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
├── contexts/       AuthContext, CollectionContext et ThemeContext
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

Backend, depuis la racine :

```powershell
python -m compileall -q api
python -m pytest api/tests
```

Les tests utilisent une base SQLite temporaire : la base `ma_collection.db` n'est pas modifiée.

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

- Le JWT est stocké dans `localStorage`, ce qui doit être expliqué en soutenance.
- Les fichiers SQLite et `.env` restent locaux et ne sont pas versionnés.

## Licence

Ce projet est distribué sous licence MIT. Voir `LICENSE`.
