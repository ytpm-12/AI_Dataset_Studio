# Cahier des charges technique

Derniere mise a jour : 04/11/2026

## Architecture officielle

AI Dataset Studio adopte une architecture client-serveur :

- frontend : React avec Vite, execute et gere avec Node.js ;
- backend : Django et Django REST Framework ;
- base relationnelle : PostgreSQL ;
- fichiers MVP : stockage local via Django, remplacable par un stockage objet ;
- traitement data : pandas, puis Polars seulement si les mesures le justifient ;
- taches asynchrones : Celery ;
- broker et resultats Celery : Redis ;
- IA : regles deterministes et Qwen3 en complement ;
- tests : tests Django, tests de services data et futurs tests frontend.

Les templates Django actuels sont un prototype transitoire. Le frontend React les
remplacera ecran par ecran sans modifier le contrat `/api/v1/`.

## Responsabilites

### Frontend Node.js

- afficher les ecrans conformes a la charte UI/UX ;
- appeler l'API REST ;
- gerer la session, le CSRF et les etats de chargement ;
- afficher clairement les erreurs et la progression des traitements ;
- ne contenir aucune regle metier critique.

### Backend Django

- authentifier et autoriser les utilisateurs ;
- valider les entrees et isoler les ressources par proprietaire ;
- orchestrer les projets, fichiers, traitements et transformations ;
- exposer une API versionnee ;
- journaliser les erreurs sans exposer de details sensibles.

### Worker Celery

- traiter les fichiers volumineux hors des requetes HTTP ;
- rendre les taches idempotentes ;
- mettre a jour le statut et la progression ;
- conserver une erreur generique cote API et les details dans les journaux.

## Modules backend

| Module | Etat | Responsabilite |
|---|---|---|
| `accounts` | operationnel | inscription, connexion, session et CSRF |
| `projects` | operationnel | projets appartenant aux utilisateurs |
| `datasets` | operationnel partiel | upload, validation et profiling |
| `processing` | operationnel partiel | suivi des traitements Celery |
| `pipelines` | a construire | definition et execution des transformations |
| `annotations` | a construire | annotation et validation humaine |
| `reports` | a construire | rapports de qualite |
| `exports` | a construire | production des fichiers de sortie |
| `ai_engine` | laboratoire non integre | recommandations hybrides |

## Contraintes actuelles

- Formats acceptes : CSV, JSON et XML.
- Taille maximale par defaut : 50 Mo.
- Profilage synchrone par defaut jusqu'a 10 Mo.
- Profilage limite par defaut a 10 000 lignes.
- Pagination API : 20 ressources par page.
- Authentification : session Django avec protection CSRF.
- Origines frontend locales autorisees : `127.0.0.1:5173` et `localhost:5173`.
- Toutes les ressources metier sont filtrees par utilisateur.

Les valeurs configurables sont documentees dans `.env.example`.

## API

- Prefixe stable actuel : `/api/v1/`.
- Contrat : `docs/05_API/API_CONTRACT.md`.
- Collection de verification : `docs/05_API/postman/AI_Dataset_Studio.postman_collection.json`.
- Toute nouvelle route doit etre livree avec documentation, tests et exemple Postman.

## Exigences de qualite

- Aucun secret ou fichier utilisateur ne doit etre commite.
- Une ressource d'un autre utilisateur doit etre invisible et retournee en `404`.
- Une erreur de validation doit retourner `400` avec des details par champ.
- Les traitements longs ne doivent pas bloquer une requete HTTP.
- Les migrations doivent etre versionnees.
- La suite de tests doit etre verte avant chaque push partage.

## Strategie IA

Le LLM ne prend pas seul les decisions de transformation. Le flux cible est :

```text
profil pandas
-> regles deterministes
-> Qwen3 pour les cas ambigus
-> validation du schema JSON
-> confirmation humaine
-> transformation
```

Le checkpoint LoRA reste experimental jusqu'a une nouvelle evaluation sur des donnees
reelles validees et separees des donnees d'entrainement.
