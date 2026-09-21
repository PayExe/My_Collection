# Authentification pas à pas

Ce guide explique comment fonctionne l'authentification de **Ma Collection** et où se trouve chaque morceau de code.

L'objectif est de comprendre le chemin complet :

```text
Inscription
    -> validation Pydantic
    -> hash bcrypt du mot de passe
    -> sauvegarde en base

Connexion
    -> recherche de l'utilisateur
    -> comparaison mot de passe/hash
    -> création d'un JWT

Route protégée
    -> lecture du token Bearer
    -> vérification du JWT
    -> récupération de l'utilisateur connecté
```

## 1. Installer les dépendances

Depuis la racine du projet `My_Collection` :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r api/requirements.txt
```

Le fichier `api/requirements.txt` contient notamment :

- `fastapi` et `uvicorn` pour l'API ;
- `sqlmodel` et `aiosqlite` pour SQLite asynchrone ;
- `passlib[bcrypt]` et `bcrypt<5` pour les mots de passe ;
- `python-jose` pour les JWT ;
- `python-dotenv` pour le fichier `.env`.

La contrainte `bcrypt<5` permet à Passlib de fonctionner correctement avec bcrypt.

## 2. Configurer le secret JWT

Copier le fichier exemple :

```powershell
Copy-Item api/.env.example api/.env
```

Puis modifier `api/.env` :

```env
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./collection.db
```

Le fichier `.env` est ignoré par Git. Il ne faut jamais publier la vraie valeur de `SECRET_KEY`.

## 3. Créer la table utilisateur

Fichier : `api/models/user.py`

Ce fichier décrit la table SQL. Il ne décrit pas directement le JSON reçu par une route.

```python
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
```

Le champ important est `hashed_password` :

```text
Mot de passe reçu : secret123
Valeur stockée    : $2b$12$...hash bcrypt...
```

Le mot de passe original ne doit jamais être enregistré.

## 4. Décrire les données avec Pydantic

Fichier : `api/schemas/auth.py`

Les schemas contrôlent les données reçues et les données renvoyées.

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=72)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
```

Les schemas ne sont pas identiques :

```text
UserCreate    -> email + password reçus à l'inscription
LoginRequest  -> email + password reçus à la connexion
UserPublic    -> id + email renvoyés publiquement
TokenResponse -> token renvoyé après connexion
```

`hashed_password` n'est volontairement pas présent dans `UserPublic`.

Avec `Field`, une requête invalide est refusée automatiquement par FastAPI avec le code `422`.

Exemple invalide :

```json
{
  "email": "a",
  "password": "123"
}
```

## 5. Hasher et vérifier les mots de passe

Fichier : `api/core/security.py`

```python
from passlib.context import CryptContext


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)
```

Lors de l'inscription :

```python
hashed_password = hash_password(payload.password)
```

Lors de la connexion :

```python
is_valid = verify_password(
    payload.password,
    user.hashed_password,
)
```

On ne compare jamais les mots de passe avec `==` et on n'utilise pas MD5 ou SHA-256 seul.

## 6. Créer et vérifier les JWT

Toujours dans `api/core/security.py` :

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from api.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_subject_from_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
```

Le token contient notamment :

```text
sub -> identifiant de l'utilisateur
exp -> date d'expiration
```

Le mot de passe n'est jamais placé dans le JWT.

## 7. Mettre la logique métier dans un service

Fichier : `api/services/auth_service.py`

Le service ne connaît pas FastAPI. Il ne contient pas de `HTTPException` et ne choisit pas les codes HTTP.

Son rôle est de :

- chercher un utilisateur par email ;
- créer un utilisateur ;
- hacher son mot de passe ;
- vérifier ses identifiants.

Exemple de recherche :

```python
async def find_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    normalized_email = normalize_email(email)
    result = await session.exec(
        select(User).where(User.email == normalized_email)
    )
    return result.one_or_none()
```

Exemple de création :

```python
async def create_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:
    normalized_email = normalize_email(email)

    if await find_user_by_email(session, normalized_email) is not None:
        raise EmailAlreadyUsedError

    user = User(
        email=normalized_email,
        hashed_password=hash_password(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

Le router transforme ensuite `EmailAlreadyUsedError` en erreur HTTP `409`.

## 8. Ouvrir une session de base de données

Fichier : `api/db/database.py`

Le moteur est asynchrone :

```python
engine = create_async_engine(DATABASE_URL, echo=False)
```

La session utilise `yield` dans `api/dependencies/database.py` :

```python
async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
```

Grâce à `Depends(get_session)`, FastAPI ouvre la session pour la requête puis la ferme automatiquement.

## 9. Créer les routes d'authentification

Fichier : `api/routers/auth.py`

On utilise `APIRouter` parce que les routes sont séparées de `main.py` :

```python
router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)
```

### Inscription

```python
@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserPublic:
    ...
```

Le fonctionnement est :

1. FastAPI lit le JSON ;
2. Pydantic crée `UserCreate` ;
3. le service vérifie si l'email existe ;
4. le mot de passe est haché ;
5. l'utilisateur est enregistré ;
6. la réponse utilise `UserPublic` ;
7. le statut est `201`.

Si l'email existe déjà, la route lève :

```python
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Email déjà utilisé",
)
```

### Connexion

```python
@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    ...
```

Le fonctionnement est :

1. chercher l'utilisateur par email ;
2. comparer le mot de passe avec le hash ;
3. refuser avec `401` si les identifiants sont faux ;
4. créer un JWT ;
5. renvoyer `TokenResponse`.

Réponse attendue :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Utilisateur connecté

```python
@router.get(
    "/me",
    response_model=UserPublic,
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    return UserPublic.model_validate(current_user)
```

Cette route ne reçoit pas d'email dans le corps. Elle récupère l'utilisateur depuis le JWT.

## 10. Protéger les routes avec `get_current_user`

Fichier : `api/dependencies/auth.py`

```python
async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    ...
```

La dépendance :

1. lit `Authorization: Bearer <token>` ;
2. décode le token ;
3. récupère l'identifiant dans `sub` ;
4. cherche l'utilisateur en base ;
5. renvoie l'utilisateur ou une erreur `401`.

Pour appeler une route protégée :

```text
Authorization: Bearer eyJ...
```

Les routes `/me/collection` et `/me/stats` réutiliseront exactement cette dépendance.

## 11. Assembler l'application

Fichier : `api/main.py`

Il n'y a pas de route métier dans `main.py`.

```python
app = FastAPI(
    title="Ma Collection API",
    lifespan=lifespan,
)

app.include_router(auth_router)
```

`main.py` s'occupe aussi du CORS, de la création des tables et du handler d'erreurs.

## 12. Lancer correctement l'API

Il faut lancer Uvicorn depuis la racine du dépôt, pas depuis le dossier `api/`.

```powershell
cd C:\Users\panto\My_Collection
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --reload
```

Si tu lances `uvicorn main:app` depuis `api/`, Python peut afficher :

```text
ModuleNotFoundError: No module named 'api'
```

## 13. Tester avec Swagger

Ouvrir :

```text
http://127.0.0.1:8000/docs
```

Tester dans cet ordre :

### Test 1 : inscription

```json
{
  "email": "alice@example.com",
  "password": "secret123"
}
```

Résultat attendu : `201`.

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

Le hash ne doit pas apparaître.

### Test 2 : doublon

Renvoyer la même inscription.

Résultat attendu : `409`.

### Test 3 : connexion

Utiliser le même email et le même mot de passe.

Résultat attendu : `200` avec un `access_token`.

### Test 4 : route protégée

Cliquer sur **Authorize** dans Swagger et saisir :

```text
Bearer <access_token>
```

Puis appeler `GET /auth/me`.

Résultat attendu :

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

### Test 5 : mauvais mot de passe

Utiliser un mauvais mot de passe lors de la connexion.

Résultat attendu : `401`.

### Test 6 : token absent

Appeler `/auth/me` sans autorisation.

Résultat attendu : `401`.

## 14. Ce qu'il faut retenir pour la soutenance

- Pydantic valide les données reçues avant l'exécution de la route.
- `Field` impose des contraintes comme une longueur minimale.
- `response_model` contrôle ce que l'API renvoie.
- Le mot de passe est haché avec bcrypt et jamais stocké en clair.
- Le JWT sert à identifier l'utilisateur connecté pendant une durée limitée.
- `Depends(get_current_user)` protège les routes privées.
- Le router gère HTTP, le service gère la logique métier et le modèle décrit la base.
- Le frontend ne doit jamais pouvoir choisir l'utilisateur dont il lit la collection.
