# 0001 - Authentification par JWT (Argon2 + OAuth2)

- **Statut** : Accepté
- **Date** : 2026-10-09
- **Décideurs** : équipe du projet Ma Collection

## Contexte

L'application doit permettre à un utilisateur de créer un compte, de se connecter
et d'accéder à des pages protégées (le catalogue n'est visible qu'une fois
connecté). Il faut donc un mécanisme d'authentification fiable, qui protège les
mots de passe et qui s'intègre naturellement à un frontend React consommant une
API FastAPI sans état.

Le projet a d'abord été développé avec une pile `passlib[bcrypt]` pour le hachage,
`python-jose` pour les tokens et `HTTPBearer` pour la lecture du token. Ce
fonctionnement marchait, mais il divergeait de la méthode enseignée et empêchait
l'utilisation du bouton **Authorize** d'OAuth2 dans la documentation Swagger
générée par FastAPI. La question est donc : **quelle pile d'authentification
retenir pour le projet ?**

Contraintes :

- Les mots de passe ne doivent jamais être stockés en clair.
- L'API doit rester *stateless* (aucun état de session côté serveur).
- La solution doit être compatible avec FastAPI et rester proche de la méthode
  vue en cours.
- La mise en œuvre doit rester simple : le projet est de taille modeste.

## Options envisagées

### Option A - Conserver passlib[bcrypt] + python-jose + HTTPBearer

- **Avantages** : aucun changement, le code existant déjà testé continue de
  fonctionner.
- **Inconvénients** : ne correspond pas à la méthode du cours ; `HTTPBearer` ne
  décrit pas le flux OAuth2, donc Swagger n'affiche pas de bouton *Authorize* ;
  deux bibliothèques (`passlib`, `python-jose`) moins récemment maintenues que
  leurs alternatives.
- **Coût** : nul à court terme, mais dette technique et écart assumé avec le
  référentiel de formation.

### Option B - Sessions serveur (cookie de session)

- **Avantages** : révocation immédiate possible (déconnexion côté serveur),
  cookie `HttpOnly` inaccessible au JavaScript, adapté aux applications rendues
  côté serveur.
- **Inconvénients** : introduit un état côté serveur (à stocker et à partager),
  alors que l'API est sans état par conception ; nécessite une protection CSRF ;
  complexifie l'architecture pour un besoin simple.
- **Coût** : élevé, en désaccord avec l'architecture actuelle.

### Option C - `pwdlib[argon2]` + `PyJWT` + `OAuth2PasswordBearer` (retenue)

- **Avantages** : Argon2 est une référence actuelle pour le hachage des mots de
  passe ; `PyJWT` est la bibliothèque JWT de référence en Python ;
  `OAuth2PasswordBearer` décrit le flux OAuth2 natif de FastAPI et active le
  bouton *Authorize* dans Swagger ; correspond exactement à la méthode du cours ;
  l'API reste sans état.
- **Inconvénients** : demande de réécrire `core/security.py` et
  `dependencies/auth.py` ainsi que de nettoyer les anciennes dépendances ; un JWT
  n'est pas révocable avant expiration sans mécanisme supplémentaire.
- **Coût** : modéré et ponctuel (migration concentrée sur quelques fichiers).

## Critères

- **Sécurité** : hachage robuste des mots de passe, signature et expiration des
  tokens vérifiées.
- **Conformité au cours** : utiliser la pile enseignée (Argon2, JWT, OAuth2).
- **Simplicité d'exploitation** : intégration directe avec FastAPI et Swagger.
- **Sans état** : aucun stockage de session côté serveur.

## Décision

Nous adoptons l'**option C** : le hachage des mots de passe se fait avec
`pwdlib[argon2]`, les tokens sont créés et lus avec **PyJWT** (algorithme
`HS256`, durée de vie de 30 minutes via `ACCESS_TOKEN_EXPIRE_MINUTES`), et la
protection des routes passe par `OAuth2PasswordBearer` et la dépendance
`get_current_user`. Les deux routes de connexion (`POST /auth/login` en JSON et
`POST /token` au format OAuth2) partagent le **même service** d'authentification.

## Conséquences

- Le token est stocké dans le `localStorage` du navigateur : c'est simple, mais
  un script malveillant qui s'exécuterait dans la page pourrait le lire. C'est le
  principal inconvénient accepté de ce choix.
- Un JWT n'est pas révocable avant son expiration : une déconnexion côté client
  efface le token, mais une fuite reste valide jusqu'à l'expiration (30 minutes).
  Si le besoin apparaît, une liste de révocation ou un *refresh token* devra être
  envisagé dans un ADR ultérieur.
- Les dépendances `passlib`, `bcrypt`, `python-jose` et `HTTPBearer` sont
  supprimées du projet ; le nettoyage est décrit dans
  `docs/plan-migration-authentification.md`.
- Swagger expose désormais le bouton **Authorize**, ce qui facilite les tests
  manuels de l'API.
