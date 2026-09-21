# Backend Ma Collection

Backend de l'application **Ma Collection**, réalisé avec FastAPI, SQLModel et SQLite.

## Lancer le backend

Depuis la racine du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r api/requirements.txt
Copy-Item api/.env.example api/.env
# Remplacer ensuite SECRET_KEY dans api/.env par une vraie valeur aleatoire
python -m uvicorn api.main:app --reload
```

Documentation interactive : http://127.0.0.1:8000/docs

Documentation détaillée de l'authentification : [`docs/authentication.md`](docs/authentication.md)

Guide pas à pas avec le code : [`docs/authentication-step-by-step.md`](docs/authentication-step-by-step.md)

Le serveur doit être lancé depuis la racine `My_Collection`. Ne lance pas `uvicorn main:app` depuis `api/`, car les imports utilisent le package `api` :

```powershell
python -m uvicorn api.main:app --reload
```

## Organisation

```text
api/
├── main.py                    # Assemble l'application, sans routes
├── seed.py                    # Peuple le catalogue de jeux vidéo
├── core/
│   ├── config.py              # Configuration et variables d'environnement
│   └── security.py            # Hash des mots de passe et JWT
├── db/
│   └── database.py            # Connexion SQLite asynchrone
├── models/
│   ├── user.py                # Table des utilisateurs
│   ├── game.py                # Table du catalogue
│   └── collection_entry.py    # Table des collections personnelles
├── schemas/
│   ├── auth.py                # Données d'inscription et de connexion
│   ├── game.py                # Données entrantes/sortantes des jeux
│   └── collection.py          # Données entrantes/sortantes des collections
├── dependencies/
│   ├── database.py            # Session de base de données
│   └── auth.py                # Utilisateur connecté et vérification JWT
├── services/
│   └── auth_service.py        # Logique d'authentification sans FastAPI
└── routers/
    ├── auth.py                # Routes /auth/*
    ├── catalog.py             # Routes publiques /items/*
    └── collection.py          # Routes protégées /me/*
```

## Rôle des fichiers

- **`main.py`** : crée l'application FastAPI, configure le CORS et inclut les routers. Il ne contient aucune route métier.
- **`routers/`** : contient les routes HTTP de l'API.
- **`models/`** : décrit les tables et relations de la base de données avec SQLModel.
- **`schemas/`** : décrit les formats JSON reçus et renvoyés par l'API.
- **`dependencies/`** : contient les fonctions utilisées avec `Depends`, notamment la session DB et l'utilisateur courant.
- **`core/`** : contient la configuration et la sécurité.
- **`db/`** : initialise le moteur SQLite asynchrone et les sessions.
- **`seed.py`** : ajoute les jeux de départ sans créer de doublons.

## Routes prévues

Chaque groupe de routes est placé dans le fichier correspondant. `main.py` ne contient pas les fonctions de route : il importe les routers et les ajoute à l'application.

### Authentification

Fichier : `routers/auth.py`

| Méthode | Route | Protection | Rôle |
|---|---|---|---|
| `POST` | `/auth/register` | Publique | Crée un compte avec un email et un mot de passe. Le mot de passe est haché avant d'être enregistré. |
| `POST` | `/auth/login` | Publique | Vérifie les identifiants et renvoie un token JWT. |
| `GET` | `/auth/me` | JWT obligatoire | Renvoie l'utilisateur connecté sans jamais renvoyer son mot de passe. |

Les modèles reçus et renvoyés par ces routes sont définis dans `schemas/auth.py`. La création et la vérification des mots de passe et des tokens sont dans `core/security.py`.

### Catalogue public

Fichier : `routers/catalog.py`

| Méthode | Route | Paramètres | Rôle |
|---|---|---|---|
| `GET` | `/items` | `q`, `categorie`, `page`, `limit` | Recherche et filtre les jeux avec pagination. |
| `GET` | `/items/{item_id}` | `item_id` dans l'URL | Renvoie le détail d'un jeu ou une erreur `404`. |

Ces routes sont publiques. Elles utilisent le modèle de base `models/game.py` et les réponses définies dans `schemas/game.py`.

### Collection authentifiée

Fichier : `routers/collection.py`

Toutes ces routes nécessitent l'utilisateur courant via `Depends(get_current_user)`.

| Méthode | Route | Paramètres / corps | Rôle |
|---|---|---|---|
| `GET` | `/me/collection` | `statut`, `tri` | Liste uniquement la collection de l'utilisateur connecté. |
| `POST` | `/me/collection` | `item_id`, `statut`, `note`, `commentaire` | Ajoute un jeu à la collection. Refuse les doublons avec `409`. |
| `PATCH` | `/me/collection/{entry_id}` | `statut`, `note`, `commentaire` | Modifie une entrée appartenant à l'utilisateur connecté. |
| `DELETE` | `/me/collection/{entry_id}` | `entry_id` dans l'URL | Supprime une entrée appartenant à l'utilisateur connecté. |
| `GET` | `/me/stats` | Aucun | Renvoie le total, la répartition par statut et la note moyenne. |

Les entrées de collection sont stockées par `models/collection_entry.py`. La réponse contient également le jeu complet dans le champ `item`.

## Où placer le code d'une route ?

Pour ajouter une route, on choisit son fichier selon son domaine :

- inscription, connexion ou utilisateur connecté : `routers/auth.py` ;
- recherche ou détail d'un jeu du catalogue : `routers/catalog.py` ;
- collection personnelle ou statistiques : `routers/collection.py`.

Une route ne doit pas contenir toute la logique dans `main.py`. Elle utilise :

1. un schema dans `schemas/` pour valider le JSON ;
2. un modèle dans `models/` pour accéder aux tables ;
3. `Depends(get_session)` pour obtenir une session DB ;
4. `Depends(get_current_user)` pour protéger une route `/me/*` ;
5. un `response_model` pour contrôler la réponse publique.

Par exemple, pour `POST /me/collection` :

```text
routers/collection.py
    -> schemas/collection.py       validation du corps reçu
    -> dependencies/auth.py        récupération de l'utilisateur connecté
    -> dependencies/database.py    ouverture de la session DB
    -> models/collection_entry.py  création de l'entrée
    -> schemas/collection.py       format de la réponse
```

## Rôle de `main.py`

`main.py` reste volontairement court. Il doit assembler l'application :

```text
création de FastAPI
configuration du CORS
enregistrement du handler d'erreur
inclusion de routers/auth.py
inclusion de routers/catalog.py
inclusion de routers/collection.py
```

Il ne doit pas contenir de `@app.get`, `@app.post`, `@app.patch` ou `@app.delete` pour les routes métier.

Les routes `/me/*` nécessitent un token JWT dans l'en-tête :

```text
Authorization: Bearer <token>
```
