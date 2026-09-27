# Théorie et fonctionnement de l'authentification

## 1. Pourquoi authentifier les utilisateurs ?

Le site « Ma Collection » permet à chaque utilisateur de gérer sa propre collection. Il faut donc savoir qui fait chaque requête.

Sans authentification, n'importe qui pourrait :

- modifier la collection d'un autre utilisateur ;
- supprimer ses jeux ;
- consulter des données privées ;
- se faire passer pour quelqu'un d'autre.

L'authentification sert donc à identifier un utilisateur et à protéger les routes `/me/*`.

Il faut distinguer :

- **identification** : l'utilisateur indique qui il est, avec son email ;
- **authentification** : il prouve son identité avec son mot de passe ;
- **autorisation** : le serveur décide ce qu'il a le droit de faire.

Le catalogue est public, mais la collection personnelle est privée.

## 2. Pourquoi ces technologies ?

### FastAPI

FastAPI sert à créer l'API REST. Il fournit notamment :

- des routes comme `POST /auth/login` ;
- la validation des données avec Pydantic ;
- les dépendances avec `Depends` ;
- l'intégration de l'authentification Bearer et de Swagger `/docs`.

### bcrypt

Un mot de passe ne doit jamais être enregistré en clair. bcrypt transforme le mot de passe en hash.

```text
mot de passe → bcrypt → hash stocké en base
```

Lors de la connexion, bcrypt vérifie le mot de passe reçu avec le hash enregistré. On n'a donc pas besoin de connaître le mot de passe original.

On utilise bcrypt plutôt qu'un simple SHA-256, car bcrypt est conçu pour être volontairement lent. Cela rend les essais massifs de mots de passe plus difficiles.

### JWT

Après une connexion réussie, l'API doit donner au frontend un moyen de prouver son identité lors des prochaines requêtes. C'est le rôle du JWT (`JSON Web Token`).

Le JWT est signé avec une `SECRET_KEY`. Le serveur peut donc vérifier qu'il vient bien de lui et qu'il n'a pas été modifié.

### React Context

Le `AuthContext` permet de partager l'état de connexion dans toute l'interface :

- l'utilisateur courant ;
- le token ;
- l'état de chargement ;
- les fonctions `signIn` et `signOut`.

### Client HTTP unique

Tous les appels passent par `apiClient.ts`. Il ajoute automatiquement :

```http
Authorization: Bearer <token>
```

Cela évite de répéter la logique d'authentification dans chaque composant React.

## 3. Fonctionnement théorique

### Inscription

L'utilisateur envoie :

```json
{
  "email": "alice@example.com",
  "password": "motdepasse123"
}
```

Le serveur :

1. valide les données ;
2. normalise l'email avec `strip().lower()` ;
3. vérifie que l'email n'est pas déjà utilisé ;
4. hash le mot de passe avec bcrypt ;
5. sauvegarde l'utilisateur.

La réponse ne contient jamais le mot de passe ni le hash :

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

### Connexion

Le frontend envoie le même type de données à :

```text
POST /auth/login
```

Le serveur :

1. cherche l'utilisateur avec son email ;
2. compare le mot de passe avec le hash bcrypt ;
3. refuse avec `401` si les identifiants sont faux ;
4. crée un JWT si la vérification réussit.

Le serveur renvoie :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Structure du JWT

Le token contient notamment :

```json
{
  "sub": "1",
  "exp": "date d'expiration"
}
```

`sub` contient l'identifiant de l'utilisateur. `exp` indique la date d'expiration.

Un JWT est composé de trois parties :

```text
header.payload.signature
```

Le payload est encodé, mais pas chiffré. Il ne faut donc jamais y placer un mot de passe. La signature sert à détecter les modifications et la durée d'expiration limite la durée de validité du token.

### Requête protégée

Pour appeler une route privée, le frontend envoie :

```http
Authorization: Bearer <token>
```

Le backend vérifie alors :

1. que le token existe ;
2. que sa signature est valide ;
3. qu'il n'est pas expiré ;
4. que son identifiant correspond à un utilisateur existant.

Si tout est correct, `get_current_user` renvoie l'utilisateur courant à la route.

## 4. Comment nous l'avons implémentée

### Backend

Les fichiers principaux sont :

```text
api/
├── core/config.py          # SECRET_KEY et durée du token
├── core/security.py        # bcrypt et JWT
├── dependencies/auth.py    # vérification du token
├── services/auth_service.py# logique métier
├── routers/auth.py         # routes register, login et me
├── schemas/auth.py         # formats JSON
└── models/user.py          # table users
```

Dans `core/security.py` :

- `hash_password()` crée un hash bcrypt ;
- `verify_password()` vérifie un mot de passe ;
- `create_access_token()` crée le JWT ;
- `get_subject_from_token()` vérifie et lit le JWT.

Dans `routers/auth.py`, les routes prévues par le contrat sont :

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Dans `dependencies/auth.py`, `get_current_user` utilise `HTTPBearer` pour récupérer le token Bearer, puis cherche l'utilisateur correspondant en base.

### Frontend

Le formulaire est dans `src/pages/AuthPage.tsx`. Il appelle :

```text
registerUser() → POST /auth/register
loginUser()    → POST /auth/login
```

Après la connexion, `AuthProvider.tsx` stocke le token dans `localStorage` et appelle `/auth/me` pour récupérer l'utilisateur connecté.

`ProtectedRoute.tsx` protège les pages privées côté interface. Si aucun utilisateur valide n'est trouvé, il redirige vers la page de connexion.

`apiClient.ts` ajoute automatiquement le token à tous les appels API.

### Parcours complet

```text
Formulaire React
    ↓
POST /auth/login
    ↓
FastAPI valide les données
    ↓
Recherche de l'utilisateur
    ↓
Vérification bcrypt
    ↓
Création du JWT
    ↓
Stockage du token côté frontend
    ↓
Authorization: Bearer <token>
    ↓
Vérification par get_current_user
    ↓
Accès à la collection personnelle
```

## 5. Déconnexion et sécurité

La déconnexion supprime actuellement le token du `localStorage` :

```ts
localStorage.removeItem("access_token")
```

Il n'y a pas besoin d'une route backend `/logout` pour cette version, car le JWT est autonome. En revanche, un token déjà volé resterait utilisable jusqu'à son expiration.

Le stockage dans `localStorage` est simple, mais une faille XSS pourrait permettre à un script de lire le token. Une alternative plus sécurisée serait un cookie `HttpOnly`, inaccessible au JavaScript.

La `SECRET_KEY` doit rester dans `.env` et ne jamais être versionnée. Le CORS est limité à `http://localhost:5173` afin que seules les requêtes du frontend de développement soient autorisées.

## 6. Remarque sur l'état actuel

Le sujet demande SQLite avec SQLModel ou SQLAlchemy asynchrone. Le code actuel utilise bien SQLAlchemy asynchrone, mais sa configuration pointe actuellement vers PostgreSQL via Docker. L'authentification elle-même fonctionne avec le même principe : base de données, bcrypt, JWT et dépendance `get_current_user`.

## 7. Explication fichier par fichier

Cette section suit le trajet réel d'une authentification, du formulaire React jusqu'à la base de données.

### Backend : assemblage et configuration

#### `api/main.py`

`main.py` est le point d'entrée de l'API. Il crée l'application FastAPI et assemble les différents éléments.

Il ne contient pas directement la logique d'inscription ou de connexion. Il s'occupe de :

1. créer l'application FastAPI ;
2. initialiser et fermer la base avec `lifespan` ;
3. configurer le CORS ;
4. inclure le router d'authentification ;
5. transformer les erreurs dans un format uniforme.

Le CORS autorise le frontend Vite :

```python
allow_origins=["http://localhost:5173"]
```

Il est limité à cette origine. On n'utilise pas `*`, car cela autoriserait n'importe quel site à appeler l'API.

Les handlers d'erreurs produisent un format que le frontend peut toujours comprendre :

```json
{
  "erreur": {
    "code": 401,
    "message": "Authentification invalide"
  }
}
```

#### `api/core/config.py`

Ce fichier centralise les paramètres de sécurité :

```text
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
DATABASE_URL
```

`SECRET_KEY` sert à signer les JWT. Elle doit rester dans `.env` et ne jamais être commitée. Si quelqu'un récupère cette clé, il pourrait fabriquer de faux tokens.

La durée du token est courte, 30 minutes par défaut. Si un token est volé, sa période d'utilisation est donc limitée.

Le fichier vérifie aussi que `SECRET_KEY` existe. L'application refuse de démarrer si elle est absente.

#### `api/.env`

Ce fichier contient les vraies valeurs locales, par exemple la clé secrète et l'adresse de la base. Il ne doit pas être versionné.

#### `api/.env.example`

Ce fichier sert de modèle. Il liste les variables nécessaires sans contenir les vrais secrets. Un développeur peut le copier pour créer son propre `.env`.

### Backend : base de données et utilisateur

#### `api/db/base.py`

Ce fichier contient la classe de base SQLAlchemy dont héritent les modèles. Elle permet à SQLAlchemy de connaître les tables du projet.

#### `api/db/database.py`

Ce fichier configure la connexion asynchrone à la base et la fabrique de sessions.

La session représente une conversation avec la base pendant une requête. Elle sert par exemple à chercher un utilisateur ou à créer un compte.

La dépendance `get_session` utilise `yield` pour ouvrir une session, la fournir à la route, puis la fermer proprement à la fin de la requête.

#### `compose.yaml`

Ce fichier lance PostgreSQL dans Docker. Il configure la base, son utilisateur, son mot de passe, son port et son volume de données.

Le sujet demande SQLite, mais la version actuelle du projet utilise PostgreSQL avec ce fichier.

#### `api/models/user.py`

Ce fichier décrit la table `users` :

```text
users
├── id
├── email
└── hashed_password
```

`email` est unique et obligatoire. `hashed_password` contient uniquement le hash bcrypt, jamais le mot de passe original.

Le modèle ne doit pas être renvoyé directement par l'API, car il contient le hash. C'est pour cela qu'on utilise `UserPublic` pour les réponses.

### Backend : schemas échangés avec le frontend

#### `api/schemas/auth.py`

Ce fichier définit les formats JSON acceptés et renvoyés par les routes d'authentification.

#### `UserCreate`

Utilisé lors de l'inscription. Il contient l'email et le mot de passe et vérifie leurs tailles avant d'appeler la logique métier.

#### `LoginRequest`

Utilisé lors de la connexion. Il est séparé de `UserCreate`, car l'inscription et la connexion sont deux opérations différentes, même si elles utilisent les mêmes champs.

#### `UserPublic`

Définit les données publiques d'un utilisateur :

```json
{
  "id": 1,
  "email": "alice@example.com"
}
```

Le hash n'est pas présent dans ce schema. Avec `response_model=UserPublic`, FastAPI filtre la réponse et évite de renvoyer le hash par erreur.

#### `TokenResponse`

Définit la réponse de connexion :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Backend : bcrypt et JWT

#### `api/core/security.py`

Ce fichier regroupe les fonctions cryptographiques afin de ne pas mettre la sécurité directement dans les routes.

#### `password_context`

```python
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

Cette configuration demande à Passlib d'utiliser bcrypt.

#### `hash_password`

Transforme le mot de passe reçu à l'inscription en hash avant la sauvegarde :

```python
def hash_password(password: str) -> str:
    return password_context.hash(password)
```

#### `verify_password`

Compare le mot de passe saisi lors de la connexion avec le hash stocké :

```python
def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)
```

#### `create_access_token`

Crée le JWT avec l'identifiant de l'utilisateur dans `sub` et sa date d'expiration dans `exp`, puis signe le token avec `SECRET_KEY`.

#### `get_subject_from_token`

Décode le JWT et vérifie sa signature et son expiration. Si le token est faux, modifié ou expiré, la fonction renvoie `None`.

### Backend : logique métier

#### `api/services/auth_service.py`

Ce fichier contient la logique métier sans dépendre directement des routes FastAPI.

#### `normalize_email`

Nettoie l'adresse avec `strip().lower()` pour éviter que des espaces ou des majuscules créent des comptes différents.

#### `find_user_by_email`

Recherche un utilisateur dans la base avec son email normalisé.

#### `create_user`

Cette fonction :

1. normalise l'email ;
2. vérifie qu'il n'existe pas déjà ;
3. hash le mot de passe ;
4. crée le modèle `User` ;
5. valide la transaction avec `commit()` ;
6. recharge l'utilisateur avec `refresh()`.

Si l'email existe déjà, elle lève `EmailAlreadyUsedError`. La route transforme ensuite cette erreur en `409 Conflict`.

La contrainte `unique=True` dans le modèle reste importante, car elle protège aussi contre deux inscriptions simultanées.

#### `authenticate_user`

Cette fonction cherche l'utilisateur et vérifie son mot de passe avec bcrypt. Elle renvoie l'utilisateur si tout est correct et `None` sinon.

### Backend : protection des routes

#### `api/dependencies/auth.py`

Ce fichier contient `get_current_user`, la dépendance utilisée par les routes privées.

```python
bearer_scheme = HTTPBearer(auto_error=False)
```

Cette dépendance lit :

```http
Authorization: Bearer eyJ...
```

`get_current_user` :

1. vérifie que le header existe ;
2. récupère le token Bearer ;
3. vérifie le JWT ;
4. lit `sub` ;
5. convertit `sub` en identifiant ;
6. cherche l'utilisateur en base ;
7. renvoie l'utilisateur courant.

En cas de problème, elle renvoie `401 Unauthorized`.

Les futures routes de collection pourront utiliser :

```python
current_user: Annotated[User, Depends(get_current_user)]
```

Elles utiliseront ainsi l'utilisateur extrait du token, et non un `user_id` envoyé par le frontend. C'est ce qui empêche un utilisateur de consulter ou modifier la collection d'un autre.

### Backend : routes HTTP

#### `api/routers/auth.py`

Ce fichier expose les trois routes du contrat :

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Le router possède le préfixe `/auth`, ce qui permet de garder `main.py` court.

#### `POST /auth/register`

La route reçoit `UserCreate`, obtient une session avec `Depends(get_session)`, puis appelle `create_user()`.

Elle renvoie :

- `201` si le compte est créé ;
- `409` si l'email est déjà pris ;
- `422` si les données sont invalides.

La réponse utilise `response_model=UserPublic`, donc aucun mot de passe ou hash ne sort de l'API.

#### `POST /auth/login`

La route reçoit `LoginRequest` et appelle `authenticate_user()`.

Si les identifiants sont invalides, elle renvoie `401`. Sinon, elle crée un token avec :

```python
create_access_token(str(user.id))
```

Puis elle renvoie `TokenResponse`.

#### `GET /auth/me`

Cette route utilise `Depends(get_current_user)`. Elle ne fait pas confiance à un identifiant fourni dans l'URL ou le corps de la requête.

Elle renvoie l'utilisateur validé par le JWT, au format `UserPublic`.

### Frontend : types et client HTTP

#### `MyCollection/src/types/api.ts`

Ce fichier décrit les objets échangés avec l'API côté TypeScript :

```ts
export interface User {
  id: number
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: "bearer"
}

export interface AuthCredentials {
  email: string
  password: string
}
```

Ces types évitent `any` et permettent de vérifier la forme des données.

`ApiError` décrit aussi le format d'erreur renvoyé par le backend.

#### `MyCollection/src/services/apiClient.ts`

`apiRequest<T>` est le client HTTP unique du frontend.

Pour chaque requête, il :

1. lit le token dans `localStorage` ;
2. crée les headers ;
3. ajoute `Content-Type: application/json` ;
4. ajoute `Authorization: Bearer <token>` si un token existe ;
5. appelle `fetch` ;
6. lit la réponse JSON ;
7. transforme les erreurs en `ApiRequestError`.

Le `<T>` indique le type attendu :

```ts
apiRequest<User>("/auth/me")
apiRequest<AuthResponse>("/auth/login", options)
```

Grâce à ce fichier, aucun composant React n'a besoin de refaire la logique du token ou des erreurs.

#### `MyCollection/src/services/authService.ts`

Ce fichier regroupe les appels liés à l'authentification.

- `registerUser()` appelle `POST /auth/register` ;
- `loginUser()` appelle `POST /auth/login` ;
- `getCurrentUser()` appelle `GET /auth/me`.

Ce service sépare les appels réseau de l'affichage des pages.

### Frontend : état de connexion

#### `MyCollection/src/contexts/auth-context.ts`

Ce fichier définit le type `AuthContextValue` et crée le contexte React.

Le contexte expose :

- `token` ;
- `user` ;
- `isLoading` ;
- `signIn` ;
- `signOut`.

#### `MyCollection/src/contexts/AuthProvider.tsx`

Le provider contient l'état réel de la session.

Au démarrage, il lit `access_token` dans `localStorage`. Si le token existe, il appelle `/auth/me` pour vérifier que la session est réellement valide.

Si cette vérification échoue, il supprime le token et remet l'utilisateur à `null`.

`signIn()` :

1. sauvegarde le token ;
2. met à jour l'état React ;
3. appelle `/auth/me` ;
4. enregistre l'utilisateur courant.

`signOut()` supprime le token et vide l'utilisateur du contexte.

#### `MyCollection/src/hooks/useAuth.ts`

Ce hook permet aux composants d'utiliser facilement le contexte :

```ts
const { user, signOut } = useAuth()
```

Il vérifie aussi que le composant est bien placé sous `AuthProvider`.

### Frontend : formulaire et routes protégées

#### `MyCollection/src/pages/AuthPage.tsx`

Cette page affiche le formulaire d'inscription ou de connexion selon `mode`.

Lors de la soumission, elle :

1. récupère l'email et le mot de passe ;
2. vérifie la confirmation du mot de passe en inscription ;
3. appelle `registerUser()` ou `loginUser()` ;
4. affiche une erreur si l'API répond avec une erreur ;
5. redirige l'utilisateur si l'opération réussit.

Après une connexion réussie, le parcours est :

```text
loginUser()
    ↓
signIn(access_token)
    ↓
navigate("/home")
```

#### `MyCollection/src/components/ProtectedRoute.tsx`

Ce composant protège les pages côté interface.

- si `isLoading` vaut `true`, il affiche un message de vérification ;
- si `user` vaut `null`, il redirige vers `/` ;
- sinon, il affiche la page avec `<Outlet />`.

Cette protection est pratique pour la navigation, mais elle ne remplace pas la protection backend. Un utilisateur peut toujours appeler l'API directement, donc les routes backend doivent aussi utiliser `get_current_user`.

#### `MyCollection/src/App.tsx`

Ce fichier déclare les routes React. Les pages privées sont placées sous `ProtectedRoute`, ce qui protège notamment `/home`, `/games` et `/game-edit` dans la version actuelle.

#### `MyCollection/src/main.tsx`

Ce fichier démarre React et place les providers autour de l'application :

```text
StrictMode
└── AuthProvider
    └── BrowserRouter
        └── App
```

Toutes les pages peuvent ainsi utiliser le contexte d'authentification et le routage.

### Documentation liée

#### `api/docs/authentication.md`

Explique les étapes prévues pour construire l'authentification backend : modèles, schemas, bcrypt, JWT, dépendances et routes.

#### `api/docs/authentication-step-by-step.md`

Présente une version plus progressive de l'implémentation.

#### `api/README.md`

Explique comment démarrer le backend et décrit le rôle des différents dossiers.

#### `MyCollection/README.md`

Décrit les fonctionnalités frontend déjà présentes et celles qui restent à faire.

## 8. Résumé simple

```text
React récupère email + mot de passe
    ↓
FastAPI valide et vérifie avec bcrypt
    ↓
FastAPI crée un JWT signé
    ↓
React stocke le token
    ↓
React envoie Bearer <token>
    ↓
FastAPI vérifie le token avec get_current_user
    ↓
La route utilise uniquement l'utilisateur authentifié
```

En résumé, React gère l'interface et conserve l'état de connexion, tandis que FastAPI reste responsable de la vraie sécurité. Le frontend peut cacher un bouton, mais seul le backend peut réellement autoriser ou refuser l'accès aux données.
