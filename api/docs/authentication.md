# Authentification complète

Cette documentation explique comment réaliser l'authentification du backend **Ma Collection** avec FastAPI, SQLModel, bcrypt et JWT.

## Objectif

L'authentification doit permettre de :

1. créer un compte avec une adresse email et un mot de passe ;
2. se connecter et recevoir un token JWT ;
3. utiliser ce token pour accéder aux routes `/me/*` ;
4. retrouver l'utilisateur connecté côté serveur ;
5. empêcher un utilisateur d'accéder à la collection d'un autre utilisateur.

Le contrat impose trois routes :

| Méthode | Route | Accès | Réponse |
|---|---|---|---|
| `POST` | `/auth/register` | Public | `201` avec `id` et `email` |
| `POST` | `/auth/login` | Public | `200` avec `access_token` et `token_type` |
| `GET` | `/auth/me` | JWT obligatoire | `200` avec `id` et `email` |

Il n'y a pas besoin d'une route backend `/logout` dans ce sujet. Le frontend se déconnecte en supprimant le token enregistré.

## Timeline de réalisation

Réalise l'authentification dans cet ordre. Vérifie chaque étape avant de continuer.

### Étape 1 — Installer et vérifier les dépendances

Installer FastAPI, Uvicorn, SQLModel, aiosqlite, Passlib, python-jose et python-dotenv.

Vérifier que l'application vide démarre avec :

```powershell
python -m uvicorn api.main:app --reload
```

Objectif : obtenir la page `/docs` sans erreur d'import.

### Étape 2 — Préparer la configuration

Créer `.env.example`, puis le `.env` local.

Définir :

- `SECRET_KEY` ;
- `ALGORITHM` ;
- `ACCESS_TOKEN_EXPIRE_MINUTES` ;
- `DATABASE_URL`.

Objectif : ne coder aucun secret directement dans Python.

### Étape 3 — Préparer la base de données

Dans `db/database.py` :

1. créer le moteur SQLite asynchrone ;
2. créer la fabrique de sessions ;
3. écrire `get_session()` avec `yield` ;
4. créer les tables au démarrage de l'application.

Objectif : pouvoir ouvrir et fermer proprement une session DB avec `Depends`.

### Étape 4 — Créer le modèle `User`

Dans `models/user.py`, créer la table avec :

- `id` ;
- `email` unique ;
- `hashed_password`.

Objectif : enregistrer un utilisateur sans jamais stocker son mot de passe en clair.

### Étape 5 — Créer les schemas

Dans `schemas/auth.py`, créer les schemas séparés :

1. données reçues à l'inscription ;
2. données reçues à la connexion ;
3. réponse publique d'un utilisateur (`id`, `email`) ;
4. réponse de connexion (`access_token`, `token_type`).

Objectif : garantir que `hashed_password` ne puisse pas sortir dans une réponse.

### Étape 6 — Implémenter bcrypt

Dans `core/security.py`, créer et tester :

1. une fonction qui transforme un mot de passe en hash ;
2. une fonction qui compare un mot de passe au hash stocké.

Objectif : vérifier que le même mot de passe est accepté et qu'un mauvais mot de passe est refusé.

### Étape 7 — Implémenter les JWT

Toujours dans `core/security.py` :

1. créer un token avec l'identifiant de l'utilisateur ;
2. ajouter une date d'expiration ;
3. signer avec `SECRET_KEY` ;
4. créer la fonction de décodage et de vérification.

Objectif : obtenir un token valide et refuser un token expiré ou modifié.

### Étape 8 — Créer `POST /auth/register`

Dans `routers/auth.py` :

1. créer l'`APIRouter` avec le préfixe `/auth` ;
2. vérifier si l'email existe déjà ;
3. hacher le mot de passe ;
4. enregistrer l'utilisateur ;
5. renvoyer `201` avec `id` et `email` ;
6. renvoyer `409` si l'email est déjà utilisé.

Objectif : créer un compte sans exposer son mot de passe.

### Étape 9 — Créer `POST /auth/login`

Dans le même router :

1. chercher l'utilisateur par email ;
2. vérifier le mot de passe ;
3. créer le JWT ;
4. renvoyer le token ;
5. renvoyer `401` si les identifiants sont invalides.

Objectif : se connecter avec le compte créé à l'étape précédente.

### Étape 10 — Créer `get_current_user`

Dans `dependencies/auth.py` :

1. récupérer le token Bearer ;
2. le décoder ;
3. retrouver l'utilisateur en base ;
4. renvoyer `401` si le token est absent, invalide ou expiré ;
5. retourner l'utilisateur connecté.

Objectif : fournir une dépendance réutilisable par toutes les routes `/me/*`.

### Étape 11 — Créer `GET /auth/me`

Utiliser `Depends(get_current_user)` dans `routers/auth.py`.

Objectif : vérifier qu'un utilisateur authentifié peut récupérer son propre profil et qu'une requête sans token est refusée.

### Étape 12 — Brancher et tester

Dans `main.py` :

1. inclure `auth_router` ;
2. démarrer le serveur ;
3. tester l'inscription ;
4. tester le doublon ;
5. tester la connexion ;
6. autoriser le token dans Swagger ;
7. tester `/auth/me` avec et sans token.

À la fin de cette étape, l'authentification est terminée. Tu peux ensuite fournir `get_current_user` aux routes `/me/collection` et `/me/stats`.

## Fichiers concernés

```text
api/
├── main.py                  # crée l'application et inclut le router
├── core/
│   ├── config.py            # SECRET_KEY et durée du token
│   └── security.py          # bcrypt et JWT
├── db/
│   └── database.py          # moteur et sessions SQLite
├── models/
│   └── user.py              # table User
├── schemas/
│   └── auth.py              # formats JSON de l'authentification
├── dependencies/
│   └── auth.py              # récupération de l'utilisateur courant
└── routers/
    └── auth.py              # routes register, login et me
```

## 1. Modèle utilisateur

`models/user.py` décrit la table SQL de l'utilisateur.

Elle doit contenir au minimum :

```text
id              identifiant primaire
email           adresse unique
hashed_password mot de passe haché avec bcrypt
```

Le champ s'appelle `hashed_password` pour rappeler qu'il ne contient jamais le mot de passe original.

La base ne doit jamais contenir :

```text
password = "motdepasse123"
```

Elle doit contenir uniquement le hash bcrypt correspondant.

## 2. Schemas d'authentification

`schemas/auth.py` décrit les formats échangés avec le frontend.

### Requête d'inscription

```json
{
  "email": "alice@example.com",
  "password": "motdepasse123"
}
```

### Réponse d'inscription

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

Il faut utiliser un schema de réponse qui ne contient pas `hashed_password`.

### Réponse de connexion

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Erreurs attendues

- email déjà utilisé : `409 Conflict` ;
- identifiants invalides : `401 Unauthorized` ;
- token absent ou invalide : `401 Unauthorized`.

## 3. Configuration secrète

`core/config.py` charge la configuration depuis `.env`.

Le fichier `.env` local contient par exemple :

```env
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./collection.db
```

Le fichier `.env` ne doit jamais être commit. Seul `.env.example`, sans vraie clé secrète, doit être versionné.

La durée du token doit rester courte. Une durée de 30 minutes est suffisante pour le projet et peut être justifiée à la soutenance.

## 4. Hash du mot de passe

`core/security.py` doit contenir deux opérations distinctes :

```text
hash_password(password)
    mot de passe en clair -> hash bcrypt

verify_password(password, hashed_password)
    mot de passe fourni + hash en base -> True ou False
```

Lors de l'inscription :

```text
password reçu
    -> hash_password(password)
    -> sauvegarde du hash dans User.hashed_password
```

Lors de la connexion :

```text
password reçu + hash en base
    -> verify_password(...)
    -> création du JWT si le résultat vaut True
```

Ne jamais faire un hash SHA-256 seul ou un hash manuel. Le sujet demande bcrypt via Passlib.

## 5. Création du JWT

Après vérification du mot de passe, `core/security.py` crée un token contenant au minimum l'identifiant ou l'email de l'utilisateur et une date d'expiration.

Flux :

```text
email + password
    -> recherche de l'utilisateur
    -> vérification bcrypt
    -> création du JWT signé avec SECRET_KEY
    -> réponse access_token
```

Le token est ensuite envoyé par le frontend avec chaque requête protégée :

```text
Authorization: Bearer eyJ...
```

Ne jamais mettre le mot de passe dans le JWT.

## 6. Dépendance `get_current_user`

`dependencies/auth.py` contient la fonction utilisée par les routes protégées.

Son rôle est de :

1. récupérer l'en-tête `Authorization` ;
2. extraire le token Bearer ;
3. décoder et vérifier le JWT ;
4. récupérer l'identifiant ou l'email du token ;
5. rechercher l'utilisateur en base ;
6. lever une erreur `401` si une étape échoue ;
7. retourner l'utilisateur courant si tout est valide.

Cette dépendance est ensuite utilisée comme ceci dans les routes `/me/*` :

```text
route protégée
    -> Depends(get_current_user)
    -> utilisateur courant
```

La collection doit toujours être filtrée avec l'identifiant de cet utilisateur. Ne jamais prendre un `user_id` envoyé par le frontend comme preuve de propriété.

## 7. Routes dans `routers/auth.py`

Le fichier doit utiliser un `APIRouter` :

```text
router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)
```

### `POST /auth/register`

Étapes de la route :

1. valider le corps avec le schema d'inscription ;
2. rechercher l'email en base ;
3. renvoyer `409` s'il existe déjà ;
4. hacher le mot de passe ;
5. créer l'utilisateur ;
6. faire `add`, `commit` et `refresh` ;
7. renvoyer le schema public utilisateur avec le statut `201`.

### `POST /auth/login`

Étapes de la route :

1. rechercher l'utilisateur par email ;
2. renvoyer `401` si l'utilisateur n'existe pas ;
3. vérifier le mot de passe avec bcrypt ;
4. renvoyer `401` si le mot de passe est faux ;
5. créer le JWT ;
6. renvoyer le token avec le statut `200`.

Utiliser le même message d'erreur pour un email inexistant et un mauvais mot de passe afin de ne pas révéler si un email est enregistré.

### `GET /auth/me`

Cette route utilise `Depends(get_current_user)`.

Elle ne reçoit pas de mot de passe et renvoie uniquement :

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

## 8. Branchement dans `main.py`

`main.py` crée une seule instance de `FastAPI` et inclut le router d'authentification.

Il ne doit pas contenir directement les décorateurs `@app.post` ou `@app.get` des routes métier.

Le router doit être inclus avec `app.include_router(...)`. Grâce au préfixe `/auth`, une route `@router.get("/me")` devient `/auth/me`.

## 9. Tester avec `/docs`

Lancer le serveur depuis la racine du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --reload
```

Ouvrir : http://127.0.0.1:8000/docs

Tester dans cet ordre :

1. `POST /auth/register` avec un nouvel email ;
2. refaire la même requête pour vérifier l'erreur `409` ;
3. `POST /auth/login` avec les bons identifiants ;
4. copier `access_token` ;
5. cliquer sur **Authorize** dans Swagger et saisir `Bearer <token>` ;
6. appeler `GET /auth/me` ;
7. tester sans token ou avec un mauvais token pour vérifier l'erreur `401`.

## 10. Erreurs fréquentes

### `router is not defined`

Dans `routers/auth.py`, il faut créer un `APIRouter`. Il ne faut pas créer une deuxième application `FastAPI` dans chaque router.

### `Could not import module api.main`

Lancer Uvicorn depuis la racine `My_Collection`, et utiliser :

```powershell
python -m uvicorn api.main:app --reload
```

### Le hash apparaît dans la réponse

Le `response_model` utilise probablement le modèle SQL directement ou un schema qui contient `hashed_password`. Créer un schema public contenant uniquement `id` et `email`.

### Une route `/me` accepte un utilisateur choisi par le frontend

La route doit utiliser `get_current_user` et prendre l'utilisateur depuis le token, pas depuis un `user_id` fourni dans la requête.

## Ressources recommandées

- FastAPI - Security : https://fastapi.tiangolo.com/tutorial/security/
- FastAPI - OAuth2 avec JWT : https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- FastAPI - Dependencies : https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI - APIRouter : https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Python-JOSE : https://python-jose.readthedocs.io/
- Passlib : https://passlib.readthedocs.io/
