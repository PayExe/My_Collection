# Fonctionnement de la base et du CRUD

Ce document explique l'organisation du backend, les relations entre les fichiers et la logique du CRUD de collection. Il ne détaille pas chaque ligne de code : il décrit le rôle des composants et le chemin suivi par une requête.

## 1. Architecture générale

Le backend suit ce flux :

```text
Client React
    ↓ HTTP + JSON
FastAPI
    ↓ router
Validation Pydantic
    ↓
Dépendances FastAPI
    ↓ session + utilisateur courant
SQLAlchemy asynchrone
    ↓
SQLite
```

Les responsabilités sont séparées :

```text
main.py                    assemblage de l'application
routers/                   routes HTTP
schemas/                   formats JSON et validation
models/                    tables SQLAlchemy
dependencies/              session DB et authentification
db/                        moteur, sessions et métadonnées
core/                      configuration et sécurité
services/                  logique métier de l'authentification
```

## 2. Pourquoi SQLite

SQLite stocke la base dans un fichier local :

```text
ma_collection.db
```

Le backend utilise la chaîne de connexion suivante :

```text
sqlite+aiosqlite:///./ma_collection.db
```

SQLite est adaptée au projet parce qu'elle ne nécessite pas de serveur séparé et respecte la contrainte du sujet sur l'accès asynchrone. Le frontend ne lit jamais directement le fichier `.db` : toutes les opérations passent par FastAPI.

Le flux est donc :

```text
React → FastAPI → SQLAlchemy → aiosqlite → SQLite
```

## 3. Initialisation de la base

### `api/db/base.py`

`Base` est la classe déclarative commune aux modèles SQLAlchemy.

Les modèles suivants en héritent :

```text
User
Game
CollectionEntry
```

SQLAlchemy enregistre leurs tables dans :

```text
Base.metadata
```

### `api/db/database.py`

Ce fichier :

- crée le moteur asynchrone ;
- crée la fabrique de sessions ;
- importe les modèles afin qu'ils soient enregistrés dans `Base.metadata` ;
- crée les tables au démarrage ;
- ferme le moteur à l'arrêt.

Les imports des modèles sont nécessaires même lorsqu'ils ne sont pas utilisés directement dans le fichier. Sans eux, SQLAlchemy peut ne pas connaître toutes les tables au moment de `Base.metadata.create_all`.

### `api/dependencies/database.py`

`get_session` ouvre une session pour une requête, la fournit à la route avec `Depends`, puis la ferme automatiquement grâce au gestionnaire de contexte asynchrone.

```text
requête HTTP
    ↓
get_session()
    ↓
session SQLAlchemy
    ↓
route
    ↓
fermeture de la session
```

## 4. Modèle de données

### Table `users`

Le modèle `User` contient :

```text
id
email
hashed_password
```

Le mot de passe original n'est jamais stocké.

### Table `games`

Le modèle `Game` représente le catalogue public :

```text
id
titre
categorie
description
image_url
annee
studio
plateforme
```

### Table `collection_entries`

Le modèle `CollectionEntry` représente l'association entre un utilisateur et un jeu :

```text
id
user_id
game_id
statut
note
commentaire
date_ajout
```

Les clés étrangères sont :

```text
collection_entries.user_id → users.id
collection_entries.game_id → games.id
```

Les relations métier sont :

```text
un utilisateur possède plusieurs entrées
un jeu peut être présent dans plusieurs collections
un utilisateur ne peut pas ajouter deux fois le même jeu
```

Cette dernière règle est protégée par la contrainte unique :

```text
(user_id, game_id)
```

La base protège également les valeurs métier avec deux contraintes : le statut doit appartenir aux trois valeurs prévues et la note doit être comprise entre 1 et 5. Les schemas Pydantic appliquent les mêmes règles avant l'accès à la base.

La vérification est également faite dans la route afin de renvoyer `409 Conflict` avec un message explicite.

## 5. Modèles et schemas

Les modèles SQLAlchemy et les schemas Pydantic n'ont pas le même rôle.

```text
Model SQLAlchemy → stockage en base
Schema Pydantic  → données reçues ou renvoyées par l'API
```

Par exemple, `CollectionEntry` possède `user_id`, car la base doit connaître le propriétaire. En revanche, le schema `CollectionCreate` ne demande pas `user_id` : le propriétaire est déduit du JWT.

Le schema de sortie `CollectionEntryPublic` expose le jeu complet dans `item` :

```json
{
  "id": 7,
  "statut": "en_cours",
  "note": 4,
  "commentaire": "A terminer",
  "date_ajout": "2026-03-14T10:22:00Z",
  "item": {
    "id": 3,
    "titre": "Wildwood Origins",
    "categorie": "Aventure",
    "description": "...",
    "image_url": "...",
    "annee": 2022,
    "studio": "Oak Studio",
    "plateforme": "Switch"
  }
}
```

## 6. Authentification et propriété

Les routes `/me/*` utilisent `get_current_user`.

Le flux est :

```text
Authorization: Bearer <token>
    ↓
vérification de la signature JWT
    ↓
lecture de l'identifiant utilisateur
    ↓
recherche dans users
    ↓
User courant fourni à la route
```

Une route de collection ne reçoit donc jamais un `user_id` choisi par le frontend.

La propriété est vérifiée côté serveur dans les requêtes SQL :

```text
CollectionEntry.id = entry_id
ET
CollectionEntry.user_id = current_user.id
```

Cette double condition empêche un utilisateur de lire, modifier ou supprimer l'entrée d'un autre utilisateur.

## 7. Lecture de la collection

`GET /me/collection` réalise une jointure entre `collection_entries` et `games`.

La requête doit :

1. filtrer sur l'utilisateur courant ;
2. joindre le jeu lié ;
3. filtrer par `statut` si le paramètre est fourni ;
4. trier par date ou par note ;
5. transformer chaque couple `CollectionEntry` + `Game` en `CollectionEntryPublic`.

Paramètres disponibles :

```text
GET /me/collection
GET /me/collection?statut=en_cours
GET /me/collection?tri=date
GET /me/collection?tri=note
```

## 8. Création d'une entrée

`POST /me/collection` reçoit :

```json
{
  "item_id": 3,
  "statut": "a_decouvrir",
  "note": 4,
  "commentaire": "À essayer ce week-end"
}
```

La note est facultative dans la requête conformément au contrat API. Lorsqu'elle est absente, le backend utilise la valeur par défaut `1`, qui reste dans l'intervalle autorisé de 1 à 5.

Le déroulement est :

1. Pydantic vérifie le statut, l'identifiant et la note.
2. `get_current_user` identifie le propriétaire.
3. La route vérifie que `Game` existe.
4. La route cherche un doublon pour ce propriétaire.
5. `CollectionEntry` est créé.
6. `date_ajout` est générée par le backend.
7. La transaction est validée avec `commit`.
8. L'entrée est relue avec son jeu.
9. La réponse est renvoyée avec le statut HTTP `201`.

Erreurs attendues :

```text
401 → token absent ou invalide
404 → jeu inexistant
409 → jeu déjà présent
422 → données invalides
```

La contrainte SQL unique est conservée comme protection supplémentaire contre deux requêtes concurrentes.

## 9. Modification d'une entrée

`PATCH /me/collection/{entry_id}` accepte des champs facultatifs :

```json
{
  "statut": "termine",
  "note": 5,
  "commentaire": "Terminé"
}
```

La route ne modifie que les champs effectivement envoyés. Elle ne modifie jamais :

```text
id
user_id
game_id
date_ajout
```

Le propriétaire est vérifié avant toute modification.

## 10. Suppression d'une entrée

`DELETE /me/collection/{entry_id}` :

1. recherche une entrée appartenant à l'utilisateur courant ;
2. renvoie `404` si elle n'existe pas ;
3. supprime la ligne ;
4. valide la transaction ;
5. renvoie `204 No Content`.

Une réponse `204` ne contient pas de JSON.

## 11. Statistiques

`GET /me/stats` calcule uniquement les données de l'utilisateur courant :

```text
total
par_statut
note_moyenne
```

Les agrégations sont faites par SQLAlchemy :

- `count` pour le total ;
- `group_by(statut)` pour la répartition ;
- `avg(note)` pour la moyenne.

Une collection vide renvoie une moyenne de `0` et des compteurs de statut à `0`.

## 12. Gestion des transactions

Les opérations d'écriture utilisent :

```text
session.add()
session.commit()
```

En cas d'erreur d'intégrité :

```text
session.rollback()
```

Le rollback remet la session dans un état utilisable et évite de conserver une transaction invalide.

## 13. Seed du catalogue

`api/seed.py` ajoute les jeux de démonstration avec une session SQLAlchemy asynchrone.

Le script :

1. crée les tables manquantes ;
2. récupère les titres déjà présents ;
3. ajoute uniquement les jeux absents ;
4. valide la transaction.

Il contient au moins 40 jeux répartis dans plusieurs catégories et peut être relancé sans créer de doublons.

Lancer le seed depuis la racine :

```powershell
.\.venv\Scripts\python.exe -m api.seed
```

## 14. Routes finales

Authentification :

```text
POST /auth/register
POST /auth/login
GET  /auth/me
POST /token
```

Catalogue :

```text
GET /items
GET /items/categories
GET /items/{item_id}
```

Collection :

```text
GET    /me/collection
POST   /me/collection
PATCH  /me/collection/{entry_id}
DELETE /me/collection/{entry_id}
GET    /me/stats
```

## 15. Vérification recommandée

Tester dans cet ordre :

1. Lancer le backend.
2. Ouvrir `/docs`.
3. Exécuter le seed.
4. Créer un utilisateur.
5. Se connecter et récupérer un JWT.
6. Autoriser le JWT dans Swagger.
7. Vérifier que la collection initiale est vide.
8. Ajouter un jeu.
9. Vérifier le doublon avec le même jeu.
10. Modifier l'entrée.
11. Tester le filtre et le tri.
12. Vérifier les statistiques.
13. Supprimer l'entrée.
14. Tester avec un deuxième utilisateur.

Le test avec deux utilisateurs est indispensable pour vérifier l'isolation des collections.
