# Authentification et routes protégées

Cette documentation explique comment le frontend React gère la connexion et empêche l'accès aux pages privées sans utilisateur authentifié.

## Parcours général

```text
Utilisateur
    -> / ou /login
    -> saisit email + mot de passe
    -> POST /auth/login
    -> reçoit un access_token
    -> token enregistré dans localStorage
    -> appel GET /auth/me
    -> utilisateur validé
    -> redirection vers /home
```

Si le token est absent, invalide ou expiré :

```text
route privée
    -> ProtectedRoute
    -> redirection vers /
```

## Organisation des fichiers

```text
src/
├── contexts/
│   ├── auth-context.ts       # état et type du contexte
│   └── AuthProvider.tsx      # token, utilisateur et session
├── hooks/
│   └── useAuth.ts            # accès au AuthContext
├── components/
│   └── ProtectedRoute.tsx    # bloque les routes privées
├── services/
│   ├── apiClient.ts          # client HTTP unique
│   └── authService.ts        # appels register, login et me
├── pages/
│   └── AuthPage.tsx          # formulaires connexion/inscription
├── App.tsx                   # déclaration des routes
└── main.tsx                  # branchement de AuthProvider
```

## `AuthProvider`

Fichier : `src/contexts/AuthProvider.tsx`

Le provider conserve l'état global de l'authentification :

- `token` : JWT courant ou `null` ;
- `user` : utilisateur courant ou `null` ;
- `isLoading` : vérification de la session en cours ;
- `signIn()` : enregistre le token et récupère l'utilisateur ;
- `signOut()` : supprime le token et l'utilisateur.

Il est placé autour de l'application dans `main.tsx` :

```tsx
<AuthProvider>
  <BrowserRouter>
    <App />
  </BrowserRouter>
</AuthProvider>
```

Au rechargement de la page, le provider lit `access_token` dans `localStorage`, puis appelle `/auth/me`. Cela permet de vérifier que le token est toujours valide.

## `useAuth`

Fichier : `src/hooks/useAuth.ts`

Les composants utilisent le contexte avec :

```tsx
const { user, isLoading, signIn, signOut } = useAuth()
```

Le hook lève une erreur si un composant est utilisé en dehors de `AuthProvider`.

## Connexion

Dans `src/pages/AuthPage.tsx` :

1. le formulaire récupère l'email et le mot de passe ;
2. `loginUser()` appelle `POST /auth/login` ;
3. le backend renvoie `access_token` ;
4. `signIn()` stocke le token ;
5. `signIn()` appelle `/auth/me` ;
6. l'utilisateur est redirigé vers `/home`.

Le formulaire n'appelle jamais `fetch` directement. Tous les appels passent par `apiClient.ts`.

## Inscription

Lors d'une inscription :

1. `registerUser()` appelle `POST /auth/register` ;
2. le compte est créé côté backend ;
3. l'utilisateur est redirigé vers `/login` ;
4. il doit ensuite se connecter pour recevoir un token.

Le backend ne renvoie pas de token lors de l'inscription dans le contrat imposé, donc la connexion est une deuxième étape.

## Client HTTP unique

Fichier : `src/services/apiClient.ts`

Le client HTTP :

- utilise l'URL `http://127.0.0.1:8000` par défaut ;
- ajoute automatiquement `Content-Type: application/json` ;
- ajoute `Authorization: Bearer <token>` si un token existe ;
- traduit le format d'erreur backend en `ApiRequestError`.

Exemple d'en-tête envoyé sur une route protégée :

```text
Authorization: Bearer eyJ...
```

## Protection des routes

Fichier : `src/components/ProtectedRoute.tsx`

Le composant vérifie l'état fourni par `useAuth()` :

```text
isLoading = true
    -> affiche "Vérification de la session..."

user = null
    -> Navigate vers /

user présent
    -> affiche la route avec Outlet
```

Dans `App.tsx`, les pages privées sont regroupées sous ce composant :

```tsx
<Route element={<ProtectedRoute />}>
  <Route path="/home" element={<HomePage />} />
  <Route path="/games" element={<GamePage />} />
  <Route path="/game-edit" element={<GameEditPage />} />
</Route>
```

Cela protège aussi l'accès direct en tapant une URL dans le navigateur. Masquer un bouton ne suffit pas à protéger une page frontend.

## Routes actuelles

### Publiques

```text
/          page de connexion
/login     redirection vers /
/register  page d'inscription
```

### Protégées

```text
/home
/games
/game-edit
```

Le sujet indique que le catalogue est public. Actuellement, `/games` est protégé volontairement selon le besoin actuel. Si le catalogue doit respecter strictement le contrat, il faudra sortir `/games` du groupe `ProtectedRoute`.

## Tester la protection

1. Lancer le backend sur `http://127.0.0.1:8000`.
2. Lancer le frontend sur `http://localhost:5173`.
3. Ouvrir une fenêtre privée du navigateur.
4. Aller directement sur `http://localhost:5173/home`.
5. Vérifier la redirection vers `/`.
6. Créer un compte puis se connecter.
7. Vérifier l'accès à `/home`.
8. Supprimer `access_token` dans le stockage local du navigateur.
9. Recharger `/home` et vérifier la redirection vers `/`.

## Déconnexion

La déconnexion consiste à appeler `signOut()` :

```text
localStorage.removeItem("access_token")
user = null
token = null
```

Il n'y a pas de route backend `/logout` dans le contrat imposé.

## Risque de `localStorage`

Le JWT est actuellement stocké dans `localStorage`, ce qui est simple pour le projet mais vulnérable si une faille XSS permet à un script de lire le stockage.

Une alternative plus sécurisée consiste à utiliser un cookie `HttpOnly`, inaccessible au JavaScript. En contrepartie, il faut gérer la protection CSRF et la configuration des cookies.
