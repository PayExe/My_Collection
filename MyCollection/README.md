# Ma Collection

Application de gestion d'une collection de jeux vidéo.

## Déjà fait

- Authentification backend : inscription, connexion, bcrypt et JWT
- Routes protégées côté frontend
- Page de connexion et d'inscription
- Structure FastAPI / React mise en place
- Client HTTP frontend

## Reste à faire

### Backend

- [ ] Créer le modèle `Game`
- [ ] Créer les routes publiques `/items`
- [ ] Ajouter recherche, filtres et pagination
- [ ] Ajouter au moins 40 jeux dans `seed.py`
- [ ] Créer les routes `/me/collection`
- [ ] Créer les statistiques `/me/stats`

### Frontend

- [ ] Afficher le catalogue des jeux
- [ ] Ajouter recherche, filtres et pagination
- [ ] Créer la page de collection
- [ ] Créer la page de statistiques
- [ ] Ajouter `CollectionContext`
- [ ] Ajouter le hook générique `useLocalStorage<T>`
- [ ] Gérer les états chargement, erreur et vide
- [ ] Finaliser le responsive mobile

### Finalisation

- [ ] Créer le README de lancement complet
- [ ] Renommer `MyCollection` en `web`
- [ ] Vérifier toutes les routes dans `/docs`
- [ ] Tester l'application sur une machine vierge
