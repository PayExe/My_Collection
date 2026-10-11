# Frontend Ma Collection

Frontend React de l'application **Ma Collection**.

## Installation

```powershell
npm install
```

## Lancement

```powershell
npm run dev
```

L'application est disponible sur http://localhost:5173.

L'API doit tourner sur http://127.0.0.1:8000. Pour changer cette adresse, définir `VITE_API_URL` avant le lancement.

## Architecture

```text
src/
├── components/       composants partagés et routes protégées
├── contexts/         AuthContext et CollectionContext
├── hooks/            hooks personnalisés
├── pages/            écrans associés aux routes
├── services/         client HTTP et services métier
├── styles/           styles par espace fonctionnel
└── types/            types manuels du contrat API
```

## Routes

Routes publiques :

```text
/                    connexion
/register            inscription
/games               catalogue
/games/:itemId       détail d'un jeu
```

Routes protégées :

```text
/home                accueil connecté
/collection          collection personnelle
/stats               statistiques
/game-edit           ajout d'une entrée
/game-edit/:entryId  modification d'une entrée
```

## Vérifications

```powershell
npm run lint
npm run build
```

Le client HTTP unique est `src/services/apiClient.ts`. Aucun composant ne réalise directement un appel `fetch`.
