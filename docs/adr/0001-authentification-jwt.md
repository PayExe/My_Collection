# 0001 - Authentification JWT et bcrypt

- **Statut** : Accepté
- **Date** : 2026-10-11
- **Décideurs** : équipe du projet Ma Collection

## Contexte

L'application doit permettre de créer un compte, de se connecter et de protéger les routes personnelles de la collection. L'API doit rester sans état côté serveur et le frontend React doit pouvoir envoyer un token avec les requêtes protégées.

Le projet impose également que les mots de passe soient hachés avec bcrypt via Passlib et qu'aucun mot de passe ne soit renvoyé par l'API.

## Décision

Nous utilisons :

- `passlib[bcrypt]` pour le hachage et la vérification des mots de passe ;
- `PyJWT` pour signer et décoder les tokens ;
- `OAuth2PasswordBearer` pour lire le token Bearer ;
- une durée d'expiration courte configurée par `ACCESS_TOKEN_EXPIRE_MINUTES` ;
- `localStorage` côté frontend pour conserver temporairement le token.

Les routes d'authentification sont :

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

La route `/token` reste disponible pour l'intégration OAuth2 de Swagger.

## Fonctionnement

Lors de l'inscription :

```text
mot de passe en clair
    ↓ bcrypt
hash enregistré dans users.hashed_password
```

Lors de la connexion :

```text
email + mot de passe
    ↓ recherche de l'utilisateur
    ↓ vérification bcrypt
    ↓ JWT signé et expirant
```

Les routes `/me/*` utilisent `get_current_user`, qui vérifie le JWT puis récupère l'utilisateur en base. Le frontend n'envoie jamais un `user_id` pour choisir le propriétaire d'une collection.

## Conséquences

- Les mots de passe ne sont jamais stockés en clair.
- Les response models publics ne contiennent pas `hashed_password`.
- Une déconnexion supprime le token côté frontend, sans route serveur dédiée.
- `localStorage` est simple mais un script exécuté par une faille XSS pourrait lire le token. Une alternative serait un cookie `HttpOnly`, avec une gestion CSRF supplémentaire.
- Une base locale créée avec une ancienne pile de hachage peut nécessiter la recréation des comptes lors d'une migration de développement.
