# Schemas d'authentification

`auth.py` décrit les JSON utilisés par les routes d'authentification :

- `UserCreate` : données reçues par `POST /auth/register` ;
- `LoginRequest` : données reçues par `POST /auth/login` ;
- `UserPublic` : réponse publique avec seulement `id` et `email` ;
- `TokenResponse` : réponse de connexion avec le JWT.

Le champ `hashed_password` n'est volontairement dans aucun schema de réponse : il ne doit jamais sortir de l'API.
