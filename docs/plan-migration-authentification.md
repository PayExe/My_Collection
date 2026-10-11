# Historique de l'authentification

Ce document conserve la trace de la migration vers la pile actuellement utilisée.

## Pile actuelle

```text
passlib[bcrypt]
bcrypt
PyJWT
OAuth2PasswordBearer
OAuth2PasswordRequestForm
```

La pile respecte la contrainte du projet : les mots de passe sont hachés avec bcrypt et les tokens JWT sont signés, vérifiés et expirants.

## Routes

```text
POST /auth/register  JSON {email, password}
POST /auth/login     JSON {email, password}
POST /token          formulaire OAuth2 username/password
GET  /auth/me        token Bearer obligatoire
```

`/auth/login` respecte le contrat du projet. `/token` permet à Swagger d'utiliser le flux OAuth2 standard.

## Vérifications

- Un mot de passe ne sort jamais d'un response model.
- Le hash est stocké uniquement dans `users.hashed_password`.
- Un token absent, invalide ou expiré renvoie `401`.
- La clé JWT et la durée d'expiration viennent du fichier `.env`.
