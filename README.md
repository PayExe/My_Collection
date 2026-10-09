# Gamefolio — Ma Collection de jeux vidéo

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-MIT-green)

**Gamefolio** est une application web qui permet de parcourir un catalogue de jeux
vidéo et de constituer sa collection personnelle, avec un compte protégé par
authentification.

- **Pour qui ?** Toute personne qui souhaite garder une trace des jeux qu'elle
  possède et découvrir de nouveaux titres.
- **Pourquoi ?** Réunir un catalogue clair, une recherche simple et une collection
  personnelle, dans une interface légère qui fonctionne dans le navigateur.
- **Comment ?** Un frontend **React + TypeScript (Vite)** qui consomme une API
  **FastAPI** protégée par **JWT** et adossée à une base **SQLite**.

## Sommaire

- [Aperçu](#aperçu)
- [Prérequis](#prérequis)
- [Installation & démarrage rapide](#installation--démarrage-rapide)
- [Démonstration](#démonstration)
- [Structure du dépôt](#structure-du-dépôt)
- [API](#api)
- [Contribution](#contribution)
- [Limites connues](#limites-connues)
- [Licence](#licence)

## Aperçu

Fonctionnalités disponibles :

- **Compte** : inscription, connexion et déconnexion sécurisées.
- **Catalogue** : liste paginée des jeux avec recherche textuelle.
- **Filtres** : sélection d'une catégorie (Action, RPG, Course, Aventure,
  Simulation, Gestion).
- **Interface** : jeu mis en avant, pagination configurable et bascule
  thème clair / thème sombre.
- **Routes protégées** : le catalogue n'est accessible qu'une fois connecté.

Les écrans « Ma collection » et l'édition d'un jeu sont en cours de développement
(voir [Limites connues](#limites-connues)).

## Prérequis

| Outil | Version conseillée | Rôle |
| --- | --- | --- |
| [Git](https://git-scm.com/) | 2.30+ | Récupérer le dépôt |
| [Python](https://www.python.org/) | 3.13 | Backend FastAPI |
| [Node.js](https://nodejs.org/) | 20+ (avec npm) | Frontend React / Vite |

Les dépendances Python sont listées dans [`api/requirements.txt`](api/requirements.txt)
et les dépendances JavaScript dans [`MyCollection/package.json`](MyCollection/package.json).
Elles sont installées automatiquement aux étapes suivantes.

## Installation & démarrage rapide

Les commandes ci-dessous sont à exécuter depuis la racine du dépôt (`My_Collection`).

### 1. Récupérer le projet

```bash
git clone https://github.com/PayExe/My_Collection.git
cd My_Collection
```

### 2. Backend (API FastAPI)

Créer et activer un environnement virtuel :

```bash
python -m venv .venv

# Windows (PowerShell / cmd)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r api/requirements.txt
```

Créer le fichier de configuration à partir du modèle :

```bash
# Windows
copy api\.env.example api\.env

# macOS / Linux
cp api/.env.example api/.env
```

Générer une clé secrète et la reporter dans `api/.env` (`SECRET_KEY=...`) :

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Remplir le catalogue et lancer l'API :

```bash
python -m api.seed
uvicorn api.main:app --reload
```

L'API écoute sur `http://127.0.0.1:8000` et sa documentation interactive est
disponible sur `http://127.0.0.1:8000/docs`.

### 3. Frontend (React + Vite)

Dans un **second terminal**, toujours depuis la racine :

```bash
cd MyCollection
npm install
npm run dev
```

L'application est accessible sur `http://localhost:5173`.

> Par défaut, le frontend appelle l'API sur `http://127.0.0.1:8000`. Pour changer
> l'adresse, créer un fichier `MyCollection/.env.local` avec
> `VITE_API_URL=http://autre-adresse:port`.

## Démonstration

Parcours complet, de l'arrivée sur le site à l'utilisation du catalogue :

1. Ouvrir `http://localhost:5173` : la page de **connexion** s'affiche.
2. Cliquer sur **S'inscrire**, saisir une adresse email et un mot de passe
   (8 caractères minimum), puis **Créer le compte**.
   → Résultat attendu : le compte est créé, la page revient sur la connexion.
3. Se **connecter** avec les identifiants créés.
   → Résultat attendu : redirection vers `/home`, l'adresse email apparaît en
   haut à droite.
4. Parcourir le **catalogue** : utiliser la barre de recherche pour filtrer par
   titre ou mot-clé, cliquer sur une catégorie dans la barre latérale.
   → Résultat attendu : la grille et le bloc « Choix du moment » se mettent à jour.
5. Changer le **nombre de jeux par page** (6, 12 ou 24) et naviguer avec
   **Précédent / Suivant**.
6. Cliquer sur l'icône **⚙ (paramètres)** pour basculer entre thème clair et
   thème sombre.
7. Cliquer sur **Se déconnecter**.
   → Résultat attendu : retour à la page de connexion, le catalogue n'est plus
   accessible sans se reconnecter.

> Astuce : ajouter ici une capture d'écran ou un GIF de l'accueil pour rendre la
> prise en main encore plus claire.

## Structure du dépôt

```text
My_Collection/
├── api/                     # Backend FastAPI
│   ├── core/                # Configuration et sécurité (JWT, Argon2)
│   ├── db/                  # Moteur et sessions SQLAlchemy (async)
│   ├── dependencies/        # Dépendances FastAPI (session, utilisateur courant)
│   ├── models/              # Modèles SQLAlchemy (User, Game, CollectionEntry)
│   ├── routers/             # Routes HTTP (auth, catalog, collection)
│   ├── schemas/             # Schémas Pydantic (entrées / sorties)
│   ├── services/            # Logique métier (authentification)
│   ├── main.py              # Point d'entrée de l'API
│   ├── seed.py              # Jeu de données du catalogue
│   └── requirements.txt     # Dépendances Python
├── MyCollection/            # Frontend React + Vite + TypeScript
│   └── src/
│       ├── components/      # Composants réutilisables (ProtectedRoute)
│       ├── contexts/        # Contexte d'authentification
│       ├── hooks/           # Hooks personnalisés (useAuth)
│       ├── pages/           # Pages (Auth, Home, Game, GameEdit, 404)
│       ├── services/        # Appels à l'API
│       ├── styles/          # Feuilles de style
│       └── types/           # Types TypeScript partagés
├── docs/                    # Documentation technique et utilisateur
│   ├── adr/                 # Décisions d'architecture (ADR)
│   └── guide-utilisateur.md # Guide pour les utilisateurs
└── README.md
```

## API

Base locale : `http://127.0.0.1:8000`. Documentation OpenAPI : `/docs`.

| Méthode | Route | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Créer un compte | Non |
| `POST` | `/auth/login` | Se connecter (JSON) | Non |
| `POST` | `/token` | Se connecter (formulaire OAuth2) | Non |
| `GET` | `/auth/me` | Profil de l'utilisateur connecté | Oui |
| `GET` | `/items` | Rechercher dans le catalogue (`q`, `categorie`, `page`, `limit`) | Non |
| `GET` | `/items/categories` | Liste des catégories disponibles | Non |
| `GET` | `/items/{item_id}` | Détail d'un jeu | Non |

Les routes protégées attendent un en-tête `Authorization: Bearer <token>`.

## Contribution

1. Créer une *issue* décrivant le besoin (bug, fonctionnalité, documentation).
2. Créer une branche dédiée en partant de `main`, nommée selon l'intention :
   `feature/…`, `fix/…` ou `docs/…`.
3. Committer avec un message clair, au format `type(scope): description`.
4. Ouvrir une *Pull Request* décrivant le contexte, le changement, l'impact et
   une checklist de vérification.
5. Faire relire la PR par un pair et itérer jusqu'à l'approbation.

Aucun commit n'est poussé directement sur `main`.

## Limites connues

- La collection personnelle (« Ma collection ») et l'édition d'un jeu ne sont pas
  encore implémentées côté interface ; les pages correspondantes sont des
  ébauches.
- Les routes de gestion de la collection (`/me/collection`, `/me/stats`) ne sont
  pas encore exposées par l'API.
- L'API n'a pas de suite de tests automatisés.
- Le token est stocké dans le `localStorage` du navigateur (voir l'ADR sur
  l'authentification pour les conséquences associées).

## Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier `LICENSE` pour le
texte complet. Sans licence explicite, le droit d'auteur s'appliquerait
automatiquement par défaut.
