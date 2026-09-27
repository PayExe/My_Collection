# Authentification : cours et projet

Ce document explique l'authentification en reprenant la méthode vue en cours, tout en l'adaptant au projet « Ma Collection ».

L'objectif est de conserver la route imposée par le sujet :

```text
POST /auth/login
```

et d'ajouter la route utilisée dans le cours :

```text
POST /token
```

Les deux routes utiliseront le même système de sécurité et le même service métier.

## 1. Authentification et autorisation

Ces deux notions sont liées, mais elles ne répondent pas à la même question.

### Authentification

L'authentification répond à la question :

> Qui êtes-vous ?

L'utilisateur prouve son identité avec un identifiant et un mot de passe.

### Autorisation

L'autorisation répond à la question :

> Avez-vous le droit de faire cette action ?

Par exemple, un utilisateur authentifié peut accéder à sa collection, mais pas à celle d'un autre utilisateur.

Le fonctionnement général est donc :

```text
Authentification
        ↓
Utilisateur identifié
        ↓
Autorisation des routes privées
```

Dans le projet :

- le catalogue est public ;
- les routes `/me/*` nécessitent une authentification ;
- le serveur doit vérifier que les données appartiennent bien à l'utilisateur connecté.

## 2. Pourquoi utiliser un token ?

Après la connexion, le serveur donne au client un token.

Un token est une information qui permet au serveur de reconnaître un client déjà authentifié. Il évite de renvoyer le mot de passe à chaque requête.

Le fonctionnement est le suivant :

```text
Première requête : email + mot de passe
        ↓
Vérification par l'API
        ↓
JWT renvoyé au client
        ↓
Requêtes suivantes : JWT uniquement
```

Le client transmet ensuite le token dans l'en-tête HTTP :

```http
Authorization: Bearer <JWT>
```

`Bearer` signifie que le client présente le token comme preuve d'authentification.

## 3. JWT

JWT signifie **JSON Web Token**. C'est un format standard pour transporter un token de connexion.

Un JWT est :

- compact ;
- signé ;
- transportable dans HTTP ;
- limité dans le temps grâce à une date d'expiration.

Sa structure est :

```text
xxxxx.yyyyy.zzzzz
```

### Header

Le header indique le type de token et l'algorithme utilisé pour la signature.

### Payload

Le payload contient les informations utiles au serveur. Dans notre projet, il contiendra notamment :

```json
{
  "sub": "1",
  "exp": 1780000000
}
```

`sub` représente l'identifiant de l'utilisateur et `exp` représente la date d'expiration.

### Signature

La signature permet de vérifier que le token n'a pas été modifié.

Le payload n'est pas chiffré. Il est seulement encodé. Il ne faut donc jamais mettre dans un JWT :

- un mot de passe ;
- un hash de mot de passe ;
- une information secrète.

## 4. Mots de passe et Argon2

Un mot de passe ne doit jamais être stocké en clair dans la base de données.

Le projet utilisera :

```text
pwdlib[argon2]
```

Argon2 sert à produire un hash sécurisé du mot de passe.

```text
Mot de passe en clair
        ↓
      Argon2
        ↓
Hash stocké dans la base
```

Pour créer le système de hash :

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
```

Pour créer un hash :

```python
hashed_password = password_hash.hash("azerty123")
```

Pour vérifier un mot de passe :

```python
password_hash.verify(
    "azerty123",
    hashed_password,
)
```

La vérification renvoie `True` si le mot de passe correspond au hash.

Le serveur ne peut pas retrouver le mot de passe original à partir du hash. Il vérifie simplement si le mot de passe fourni correspond.

## 5. Principe de connexion

Le principe vu en cours est :

```text
1. Client → API : username + password
2. API : recherche de l'utilisateur
3. API : vérification du mot de passe
4. API → Client : JWT
5. Client → API : Authorization: Bearer <JWT>
```

Dans notre projet, l'identifiant est un email. Pour la route du cours, l'email sera envoyé dans le champ `username`, car `OAuth2PasswordRequestForm` utilise ce nom.

## 6. Les deux routes de connexion

Le sujet impose `/auth/login` avec du JSON. Le cours utilise `/token` avec un formulaire OAuth2.

Nous gardons donc les deux routes.

### Route imposée par le projet : `/auth/login`

Requête :

```http
POST /auth/login
Content-Type: application/json
```

Corps :

```json
{
  "email": "alice@example.com",
  "password": "monmotdepasse"
}
```

Cette route respecte exactement le contrat d'API du sujet.

### Route vue en cours : `/token`

Requête :

```http
POST /token
Content-Type: application/x-www-form-urlencoded
```

Corps :

```text
username=alice@example.com&password=monmotdepasse
```

FastAPI récupère ces données grâce à :

```python
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

form_data: OAuth2PasswordRequestForm = Depends()
```

Les deux routes appelleront le même service :

```text
/auth/login ─┐
             ├──> recherche utilisateur
/token ──────┘    vérification Argon2
                  création JWT
```

Il n'y aura donc pas deux systèmes d'authentification différents.

## 7. OAuth2PasswordBearer

Pour récupérer le token Bearer, le cours utilise :

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)
```

Cette dépendance lit l'en-tête :

```http
Authorization: Bearer <JWT>
```

Une route peut alors récupérer le token avec :

```python
token: str = Depends(oauth2_scheme)
```

Le nom `tokenUrl="token"` permet aussi à Swagger de connaître la route de connexion OAuth2.

## 8. Récupérer l'utilisateur connecté

La fonction `get_current_user` reçoit le token grâce à `OAuth2PasswordBearer`.

Son rôle est de :

1. récupérer le token Bearer ;
2. décoder le JWT avec la clé secrète ;
3. vérifier sa signature ;
4. vérifier son expiration ;
5. récupérer `sub` ;
6. chercher l'utilisateur en base ;
7. renvoyer l'utilisateur connecté.

Si le token est absent, invalide ou expiré, la fonction renvoie `401`.

Exemple :

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    user_id = payload.get("sub")
    return find_user(user_id)
```

Dans la version réelle, cette fonction sera asynchrone et utilisera une session de base de données.

## 9. Protéger une route

Une route publique ne dépend pas de `get_current_user`.

Une route privée ajoute :

```python
@router.get("/me/collection")
async def get_collection(
    current_user: User = Depends(get_current_user),
):
    ...
```

`Depends(get_current_user)` force l'authentification.

```text
Sans token
    ↓
401 Unauthorized

Avec un token valide
    ↓
Utilisateur connecté transmis à la route
```

Pour modifier ou supprimer une entrée, le serveur devra également vérifier que l'entrée appartient à `current_user`.

## 10. Fichiers concernés dans le projet

```text
api/
├── core/
│   ├── config.py       # clé JWT, algorithme, expiration
│   └── security.py     # Argon2 et JWT
├── dependencies/
│   ├── auth.py         # OAuth2PasswordBearer et utilisateur courant
│   └── database.py     # session DB avec Depends
├── models/
│   └── user.py         # utilisateur et hashed_password
├── schemas/
│   └── auth.py         # inscription, login et réponse token
├── services/
│   └── auth_service.py # recherche, création et vérification utilisateur
└── routers/
    └── auth.py         # /auth/register, /auth/login, /token et /auth/me
```

## 11. À retenir pour la soutenance

```text
JWT                 = format du token
Bearer              = manière de transmettre le token
OAuth2PasswordForm  = récupération du formulaire username/password
OAuth2PasswordBearer= récupération du token Bearer
Depends()           = injection des dépendances et protection des routes
Argon2              = hash des mots de passe
PyJWT               = création et vérification des JWT
```

La phrase importante est :

> Le client s'authentifie une fois avec son identifiant et son mot de passe, puis il utilise un JWT Bearer pour accéder aux routes protégées. Le backend vérifie ce JWT grâce à `Depends(get_current_user)` avant d'autoriser l'action.
