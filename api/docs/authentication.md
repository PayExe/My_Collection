# Documentation de l'authentification

La documentation détaillée se trouve dans :

- [`../../docs/authentification-cours-et-projet.md`](../../docs/authentification-cours-et-projet.md) ;
- [`../../docs/plan-migration-authentification.md`](../../docs/plan-migration-authentification.md).

Le backend utilise `pwdlib[argon2]` pour les mots de passe, `PyJWT` pour les JWT, `OAuth2PasswordBearer` pour les tokens Bearer et `OAuth2PasswordRequestForm` pour la route `/token`.
