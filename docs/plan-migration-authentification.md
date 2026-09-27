# Plan de migration de l'authentification

Ce document décrit le nettoyage de l'ancien système et la mise en place du système vu en cours.

Objectif :

- utiliser `pwdlib[argon2]` pour les mots de passe ;
- utiliser `PyJWT` pour les tokens ;
- utiliser `OAuth2PasswordBearer` pour les tokens Bearer ;
- utiliser `OAuth2PasswordRequestForm` avec `/token` comme dans le cours ;
- conserver `/auth/login` pour respecter le contrat du projet ;
- utiliser la même logique derrière `/token` et `/auth/login`.

## 1. État actuel

Le système actuel utilise :

```text
passlib[bcrypt]
bcrypt
python-jose
HTTPBearer
POST /auth/login avec du JSON
```

Les fichiers principaux actuels sont :

```text
api/core/security.py
api/dependencies/auth.py
api/services/auth_service.py
api/routers/auth.py
api/schemas/auth.py
api/models/user.py
```

Le système actuel fonctionne, mais il ne correspond pas à la méthode vue en cours.

## 2. Architecture cible

L'architecture finale sera :

```text
                         ┌─────────────────────┐
POST /auth/login ────────┤                     │
JSON email + password    │                     │
                         │  Service commun    │──> Argon2
POST /token ─────────────┤  authentification   │
Form username + password │                     │──> JWT
                         └─────────────────────┘
                                      ↓
                         Authorization: Bearer JWT
                                      ↓
                         OAuth2PasswordBearer
                                      ↓
                         Depends(get_current_user)
```

Les deux routes ne doivent pas contenir deux copies différentes de la logique de connexion.

## 3. Étape 1 : remplacer les dépendances

### Anciennes dépendances

À retirer de `api/requirements.txt` :

```text
passlib[bcrypt]
bcrypt<5
python-jose[cryptography]
```

### Nouvelles dépendances

À ajouter :

```text
PyJWT
pwdlib[argon2]
```

À conserver :

```text
python-multipart
```

`python-multipart` est nécessaire pour que `OAuth2PasswordRequestForm` puisse lire les formulaires envoyés à `/token`.

## 4. Étape 2 : modifier la configuration

### Fichier : `api/core/config.py`

Conserver les variables :

```text
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
```

La clé doit continuer à venir du fichier `.env` et ne doit jamais être écrite directement dans le code.

Exemple :

```text
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

La durée courte du token doit être conservée et justifiée par la sécurité : un token volé expirera rapidement.

## 5. Étape 3 : remplacer `core/security.py`

### Ancien fonctionnement

Le fichier utilise actuellement :

```python
from passlib.context import CryptContext
from jose import jwt
```

### Nouveau fonctionnement

Le fichier devra utiliser :

```python
import jwt
from pwdlib import PasswordHash
```

Créer l'outil de hash :

```python
password_hash = PasswordHash.recommended()
```

Créer les fonctions :

```python
def hash_password(password: str) -> str:
    return password_hash.hash(password)
```

```python
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
```

Créer le JWT avec :

```python
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
```

Créer aussi une fonction de lecture du token avec `jwt.decode`.

Elle devra vérifier :

- la signature ;
- l'algorithme ;
- l'expiration ;
- la présence de `sub`.

Les erreurs JWT devront être transformées en erreur d'authentification `401` dans la dépendance.

## 6. Étape 4 : modifier la dépendance d'authentification

### Fichier : `api/dependencies/auth.py`

### Ancien fonctionnement

Le fichier utilise actuellement :

```python
HTTPBearer
```

### Nouveau fonctionnement

Utiliser l'outil du cours :

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)
```

Puis récupérer le token dans `get_current_user` :

```python
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    ...
```

La fonction devra :

1. décoder le token avec PyJWT ;
2. récupérer `sub` ;
3. convertir `sub` en identifiant ;
4. chercher l'utilisateur en base ;
5. renvoyer `401` si le token est invalide ou l'utilisateur absent ;
6. renvoyer l'utilisateur si tout est valide.

Cette fonction restera la dépendance utilisée par les futures routes `/me/*`.

## 7. Étape 5 : garder un service commun

### Fichier : `api/services/auth_service.py`

Le service doit rester indépendant de FastAPI.

Il conservera les fonctions :

```text
normalize_email()
find_user_by_email()
create_user()
authenticate_user()
```

`create_user()` devra utiliser le nouveau `hash_password()` basé sur Argon2.

`authenticate_user()` devra utiliser le nouveau `verify_password()` basé sur Argon2.

Le service ne doit pas créer lui-même le JWT. La création du token reste une responsabilité de la route ou d'une fonction de sécurité dédiée.

Le fonctionnement sera :

```text
email + password
    ↓
find_user_by_email()
    ↓
verify_password()
    ↓
User ou None
```

## 8. Étape 6 : conserver et ajouter les routes

### Fichier : `api/routers/auth.py`

#### Route conservée : `POST /auth/login`

Cette route respecte le sujet et reçoit du JSON :

```json
{
  "email": "alice@example.com",
  "password": "monmotdepasse"
}
```

Elle continuera à utiliser `LoginRequest`.

Son fonctionnement sera :

```text
LoginRequest
    ↓
authenticate_user()
    ↓
create_access_token(user.id)
    ↓
TokenResponse
```

#### Route ajoutée : `POST /token`

Cette route reproduit le cours :

```python
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    ...
```

Le formulaire contient :

```text
username=alice@example.com
password=monmotdepasse
```

Même si le champ s'appelle `username`, sa valeur sera l'email du projet.

La route appellera le même service que `/auth/login` :

```text
form_data.username
    ↓
authenticate_user(session, form_data.username, form_data.password)
```

Les deux routes renverront le même format :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Route conservée : `GET /auth/me`

Cette route utilisera le nouveau `get_current_user`, qui lui-même utilisera `OAuth2PasswordBearer`.

## 9. Étape 7 : vérifier le modèle utilisateur

### Fichier : `api/models/user.py`

Le modèle peut conserver :

```text
id
email
hashed_password
```

Le champ `hashed_password` est un bon nom, car il rappelle que le mot de passe original n'est pas stocké.

Il ne faut pas renommer obligatoirement `email` en `username`, car le contrat du projet demande `email`.

La différence sera uniquement au niveau de `/token` :

```text
username du formulaire OAuth2 = email du modèle User
```

## 10. Étape 8 : vérifier les schemas

### Fichier : `api/schemas/auth.py`

Conserver :

```text
UserCreate
LoginRequest
UserPublic
TokenResponse
```

`LoginRequest` est nécessaire pour `/auth/login`.

`OAuth2PasswordRequestForm` remplace le schema JSON uniquement pour `/token`. Il ne faut donc pas essayer de l'utiliser pour `/auth/login`, car cela casserait le contrat imposé.

`UserPublic` doit continuer à ne contenir que :

```text
id
email
```

Le hash ne doit apparaître dans aucune réponse.

## 11. Étape 9 : vérifier `main.py` et Swagger

### Fichier : `api/main.py`

Le router d'authentification doit rester inclus :

```python
app.include_router(auth_router)
```

La route `/token` apparaîtra dans Swagger. Grâce à `OAuth2PasswordBearer(tokenUrl="token")`, Swagger pourra proposer le bouton d'autorisation OAuth2.

Il faudra vérifier que :

- `/auth/login` est toujours visible ;
- `/token` est visible ;
- `/auth/me` affiche l'authentification Bearer ;
- le bouton **Authorize** fonctionne ;
- un token valide permet d'appeler `/auth/me`.

## 12. Étape 10 : nettoyage de l'ancien système

Une fois le nouveau système fonctionnel :

1. supprimer les imports `passlib` ;
2. supprimer les imports `bcrypt` ;
3. supprimer les imports `jose` ;
4. supprimer `HTTPBearer` ;
5. supprimer l'ancien `password_context` ;
6. supprimer l'ancien décodage avec `python-jose` ;
7. vérifier qu'aucune route n'utilise encore l'ancien système ;
8. mettre à jour `requirements.txt` ;
9. réinstaller les dépendances ;
10. rechercher les anciennes références avec une recherche globale.

Recherche à effectuer :

```text
passlib
bcrypt
python-jose
HTTPBearer
CryptContext
```

Après le nettoyage, il ne doit rester que :

```text
pwdlib
argon2
PyJWT
OAuth2PasswordBearer
OAuth2PasswordRequestForm
```

## 13. Tests à réaliser

### Inscription

```text
POST /auth/register
```

Vérifier :

- réponse `201` ;
- utilisateur créé ;
- mot de passe non visible dans la base en clair ;
- hash absent de la réponse ;
- doublon email = `409`.

### Connexion avec la route du sujet

```text
POST /auth/login
```

Vérifier :

- JSON accepté ;
- bons identifiants = JWT ;
- mauvais identifiants = `401`.

### Connexion avec la route du cours

```text
POST /token
```

Vérifier :

- formulaire `username/password` accepté ;
- email utilisé comme valeur de `username` ;
- bons identifiants = JWT ;
- mauvais identifiants = `401`.

### Route protégée

Tester `GET /auth/me` :

```text
Sans token       → 401
Token incorrect  → 401
Token expiré     → 401
Token valide     → 200
```

## 14. Résultat final attendu

Après la migration :

```text
POST /auth/register
    ↓
Création d'un utilisateur avec hash Argon2

POST /auth/login
    ↓
Connexion JSON conforme au sujet

POST /token
    ↓
Connexion formulaire conforme au cours

Les deux routes
    ↓
Même service
    ↓
Même création JWT avec PyJWT
    ↓
Même protection avec OAuth2PasswordBearer
    ↓
Même get_current_user
```

Cette solution permet de montrer la méthode du cours tout en conservant le contrat demandé pour le projet.
