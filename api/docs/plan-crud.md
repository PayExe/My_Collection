# Plan de réalisation du CRUD

Ce document décrit la réalisation du CRUD de la collection personnelle.

Le CRUD concerne les entrées de collection d'un utilisateur authentifié, et non le catalogue public des jeux.

## Architecture retenue

Les modèles backend utilisent actuellement SQLAlchemy asynchrone et héritent de `api.db.base.Base`. Le CRUD doit donc rester cohérent avec cette architecture : aucun modèle CRUD ne doit utiliser `SQLModel`.

Le PDF impose une base SQLite asynchrone. Avant le lancement final, la configuration et les dépendances devront donc utiliser SQLite avec `aiosqlite` au lieu de la configuration PostgreSQL actuellement présente sur la branche distante. Cette décision doit être coordonnée avec le binôme.

## 1. Périmètre

Routes concernées :

| Opération | Méthode | Route |
|---|---|---|
| Lire la collection | `GET` | `/me/collection` |
| Ajouter une entrée | `POST` | `/me/collection` |
| Modifier une entrée | `PATCH` | `/me/collection/{entry_id}` |
| Supprimer une entrée | `DELETE` | `/me/collection/{entry_id}` |
| Lire les statistiques | `GET` | `/me/stats` |

Le catalogue public possède ses propres routes en lecture seule :

```text
GET /items
GET /items/{item_id}
```

## 2. Modèle de données

Le projet utilise trois objets principaux :

```text
User
Game
CollectionEntry
```

Une `CollectionEntry` relie un utilisateur à un jeu et contient :

```text
id
user_id
game_id
statut
note
commentaire
date_ajout
```

Relations :

```text
User 1 ─── plusieurs CollectionEntry
Game 1 ─── plusieurs CollectionEntry
```

Un même jeu peut appartenir à plusieurs utilisateurs. En revanche, un même utilisateur ne peut pas ajouter deux fois le même jeu.

La combinaison suivante doit donc être unique :

```text
(user_id, game_id)
```

## 3. Ordre de réalisation

### Étape 1 : définir le modèle `Game`

Le modèle du catalogue doit être défini avant la collection, car chaque entrée doit pointer vers un jeu existant.

Champs prévus :

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

Le modèle doit être validé avec le contrat API et les types frontend.

### Étape 2 : créer le modèle `CollectionEntry`

Créer la table qui stocke les entrées personnelles.

Contraintes à respecter :

- `user_id` référence un utilisateur existant ;
- `game_id` référence un jeu existant ;
- `statut` vaut `a_decouvrir`, `en_cours` ou `termine` ;
- `note` est comprise entre 1 et 5 ;
- `commentaire` est facultatif ;
- `date_ajout` est générée par le serveur ;
- `(user_id, game_id)` est unique.

### Étape 3 : enregistrer les modèles dans SQLAlchemy

Les modèles `Game` et `CollectionEntry` héritent de `Base` dans `api/db/base.py`. Ils doivent être importés avant l'appel à `Base.metadata.create_all`.

Le démarrage suit ce flux :

```text
démarrage FastAPI
    ↓
import des modèles
    ↓
création des tables de la base configurée
```

### Étape 4 : créer les schemas

Les schemas d'entrée et de sortie doivent être séparés.

Pour un ajout, le frontend envoie :

```text
item_id
statut
note
commentaire
```

Le frontend ne doit pas fournir :

```text
user_id
date_ajout
```

Ces valeurs sont contrôlées par le backend.

Pour une modification, `statut`, `note` et `commentaire` sont facultatifs. Un champ absent signifie qu'il ne faut pas le modifier.

### Étape 5 : implémenter `GET /me/collection`

La route doit :

1. vérifier le token JWT ;
2. récupérer l'utilisateur courant avec `get_current_user` ;
3. filtrer les entrées avec son identifiant ;
4. charger le jeu associé ;
5. appliquer le filtre `statut` si présent ;
6. appliquer le tri `date` ou `note` si présent ;
7. retourner une liste d'entrées.

La requête ne doit jamais récupérer toutes les collections pour filtrer ensuite côté frontend.

### Étape 6 : implémenter `POST /me/collection`

Flux de création :

```text
requête JSON
    ↓
validation du schema
    ↓
identification de l'utilisateur par JWT
    ↓
vérification de l'existence du jeu
    ↓
vérification du doublon
    ↓
création de l'entrée
    ↓
génération de date_ajout
    ↓
commit de la transaction
    ↓
réponse avec le jeu imbriqué
```

Réponses attendues :

| Situation | Code |
|---|---:|
| Entrée créée | `201` |
| Jeu inexistant | `404` |
| Jeu déjà présent | `409` |
| Token absent ou invalide | `401` |
| Données invalides | `422` |

### Étape 7 : implémenter `PATCH /me/collection/{entry_id}`

La route doit :

1. rechercher l'entrée ;
2. vérifier qu'elle existe ;
3. vérifier qu'elle appartient à l'utilisateur courant ;
4. appliquer uniquement les champs présents ;
5. revalider le statut et la note ;
6. sauvegarder la modification ;
7. retourner l'entrée mise à jour.

Un utilisateur ne doit jamais pouvoir modifier l'entrée d'un autre utilisateur.

### Étape 8 : implémenter `DELETE /me/collection/{entry_id}`

La route doit :

1. rechercher l'entrée ;
2. vérifier sa propriété ;
3. la supprimer ;
4. valider la transaction ;
5. retourner `204 No Content`.

Une réponse `204` ne contient pas de corps JSON.

### Étape 9 : implémenter `GET /me/stats`

Les statistiques doivent concerner uniquement l'utilisateur courant :

```text
total
par_statut
note_moyenne
```

Exemple de résultat :

```text
total: 10
par_statut:
  a_decouvrir: 4
  en_cours: 3
  termine: 3
note_moyenne: 4.2
```

### Étape 10 : inclure le router

Le router de collection doit être inclus dans `api/main.py` avec les autres routers.

Sans cette inclusion, les fonctions peuvent exister dans `routers/collection.py` mais les routes ne seront pas accessibles par FastAPI.

## 4. Fonctionnement d'une requête

Exemple : ajout d'un jeu dans la collection.

```text
React
    ↓ POST /me/collection
client HTTP
    ↓ Authorization: Bearer <token>
FastAPI
    ↓ validation du schema
get_current_user
    ↓ utilisateur connecté
route collection
    ↓ vérifications métier
SQLAlchemy / AsyncSession
    ↓
base de données configurée
    ↓
réponse JSON
```

Le `user_id` utilisé par la requête vient toujours du JWT vérifié, jamais d'une valeur fournie par le frontend.

## 5. Tests manuels dans `/docs`

Tester dans cet ordre :

1. Créer un utilisateur avec `POST /auth/register`.
2. Se connecter avec `POST /auth/login`.
3. Cliquer sur `Authorize` et renseigner le token.
4. Vérifier `GET /auth/me`.
5. Vérifier que `GET /me/collection` retourne une liste vide.
6. Ajouter un jeu avec `POST /me/collection`.
7. Refaire le même ajout et vérifier la réponse `409`.
8. Modifier le statut avec `PATCH`.
9. Modifier la note et le commentaire.
10. Vérifier le filtre et le tri de la collection.
11. Vérifier `GET /me/stats`.
12. Supprimer l'entrée avec `DELETE`.
13. Vérifier que l'entrée n'existe plus.
14. Créer un second utilisateur.
15. Vérifier que le second utilisateur ne voit pas la collection du premier.

## 6. Branchement frontend

Le frontend ne doit pas utiliser `fetch` directement dans les pages.

Créer ensuite un service dédié, par exemple :

```text
src/services/collectionService.ts
```

Ce service appellera :

```text
getCollection()
addToCollection()
updateCollectionEntry()
deleteCollectionEntry()
getStats()
```

Les pages pourront ensuite utiliser ce service :

```text
CollectionPage.tsx
GameEditPage.tsx
StatsPage.tsx
```

La page `GameEditPage` pourra gérer l'ajout et la modification d'une entrée. Une page distincte devra afficher la collection complète.

## 7. Répartition des fichiers

Fichiers principalement liés au CRUD :

```text
api/models/collection_entry.py
api/schemas/collection.py
api/routers/collection.py
web/src/pages/CollectionPage.tsx
web/src/pages/GameEditPage.tsx
web/src/services/collectionService.ts
```

Fichiers partagés à modifier en coordination avec le binôme :

```text
api/main.py
api/db/database.py
api/models/game.py
api/schemas/game.py
web/src/App.tsx
web/src/types/api.ts
```

## 8. Validation finale

Avant de considérer le CRUD terminé, vérifier :

- toutes les routes du contrat existent ;
- les codes HTTP sont corrects ;
- les routes `/me/*` exigent un JWT ;
- un utilisateur ne voit que sa collection ;
- les doublons sont refusés ;
- les notes et statuts sont validés ;
- les mots de passe ne sortent jamais de l'API ;
- les erreurs utilisent le format `{ "erreur": { ... } }` ;
- les réponses contiennent le jeu imbriqué ;
- les tests fonctionnent avec au moins deux utilisateurs ;
- le router est bien inclus dans `main.py`.
