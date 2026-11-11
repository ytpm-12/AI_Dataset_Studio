# Contrat d'API - AI Dataset Studio

Version : `v1`  
Derniere mise a jour : `04/11/2026`
URL locale : `http://127.0.0.1:8000/api/v1`

Ce document recense uniquement les routes actuellement implementees. Toute nouvelle
route doit etre ajoutee ici dans le meme increment que son code et ses tests.

Collection Postman :
`docs/05_API/postman/AI_Dataset_Studio.postman_collection.json`.

## Charte API

### Versionnement et URLs

- Toutes les routes metier sont prefixees par `/api/v1/`.
- Les collections utilisent un nom pluriel : `/projects/`, `/uploads/`, `/jobs/`.
- Les URLs se terminent par `/`, conformement a Django REST Framework.
- Une rupture de compatibilite exige une nouvelle version majeure, par exemple `/api/v2/`.
- L'ajout d'un champ de reponse optionnel ne constitue pas une rupture.

### Methodes HTTP

| Methode | Usage |
|---|---|
| `GET` | Lire une ressource ou une collection sans effet de bord |
| `POST` | Creer une ressource ou declencher une action explicite |
| `PUT` | Remplacer toutes les proprietes modifiables d'une ressource |
| `PATCH` | Modifier seulement les proprietes fournies |
| `DELETE` | Supprimer une ressource lorsque cette action sera disponible |

### Formats et nommage

- Les requetes et reponses utilisent JSON, sauf l'upload qui utilise `multipart/form-data`.
- Les champs JSON utilisent `snake_case`.
- Les identifiants sont des entiers positifs.
- Les dates sont retournees au format ISO 8601 avec fuseau horaire.
- Les valeurs d'enumeration sont stables, en minuscules et en anglais technique.
- Les libelles affichables peuvent etre traduits et ne doivent pas servir de cle metier.

### Codes de succes

| Code | Usage |
|---|---|
| `200` | Lecture ou modification reussie |
| `201` | Ressource creee |
| `204` | Action reussie sans corps de reponse |

### Erreurs

- Une erreur de validation retourne `400` avec un objet indexe par champ.
- Une requete sans session ou avec un CSRF invalide retourne `403`.
- Une ressource inexistante ou appartenant a un autre utilisateur retourne `404`.
- Une erreur `500` ne doit jamais exposer une trace Python ou un secret en production.

Exemple de validation :

```json
{
  "file": ["Format non supporte. Formats acceptes: .csv, .json, .xml."]
}
```

### Securite et propriete

- L'authentification actuelle repose sur une session Django et un jeton CSRF.
- Le frontend Node.js doit envoyer les cookies avec `credentials: "include"`.
- Toute route metier filtre les donnees par l'utilisateur connecte.
- Les mots de passe, cookies, jetons CSRF et chemins internes ne sont jamais journalises.
- Aucun endpoint ne doit accepter un `owner` fourni par le client.

### Pagination et filtres

- Les listes sont paginees et retournent `count`, `next`, `previous` et `results`.
- La taille actuelle est fixee a 20 elements par page.
- Les filtres utilisent la query string, par exemple `?status=processing`.
- Un filtre invalide retourne `400` au lieu d'etre silencieusement ignore.

### Cycle de livraison d'un endpoint

Un endpoint est considere comme disponible uniquement lorsque :

1. son URL et ses permissions sont implementees ;
2. ses cas nominaux et erreurs principales sont testes ;
3. il est documente dans ce fichier ;
4. une requete correspondante existe dans la collection Postman ;
5. une interface React est ajoutee lorsque la fonction est destinee a l'utilisateur final.

## Authentification et CSRF

L'API utilise une session Django. Postman doit conserver automatiquement les cookies
`csrftoken` et `sessionid` recus par le serveur.

Pour chaque requete `POST`, `PUT` ou `PATCH` :

1. Appeler `GET /auth/csrf/`
2. Copier la valeur `csrfToken` de la reponse.
3. Ajouter l'en-tete `X-CSRFToken: <valeur>` a la requete.
4. Conserver les cookies dans le meme environnement Postman.

Toutes les routes sont authentifiees, sauf `csrf`, `register` et `login`.

## Format commun des listes

Les listes sont paginees par 20 elements :

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": []
}
```

Le parametre `?page=2` permet de changer de page.

## Routes disponibles

| Methode | Route | Authentification | Description |
|---|---|---|---|
| GET | `/auth/csrf/` | Non | Obtenir le jeton CSRF |
| POST | `/auth/register/` | Non | Creer un compte et ouvrir une session |
| POST | `/auth/login/` | Non | Ouvrir une session |
| GET | `/auth/me/` | Oui | Lire l'utilisateur connecte |
| POST | `/auth/logout/` | Oui | Fermer la session |
| GET | `/projects/` | Oui | Lister ses projets |
| POST | `/projects/` | Oui | Creer un projet |
| GET | `/projects/{id}/` | Oui | Lire un projet |
| PUT/PATCH | `/projects/{id}/` | Oui | Modifier un projet |
| GET | `/uploads/` | Oui | Lister ses fichiers |
| POST | `/uploads/` | Oui | Importer un fichier CSV, JSON ou XML |
| GET | `/uploads/{id}/` | Oui | Lire un fichier et son profil |
| GET | `/uploads/{id}/preview/` | Oui | Lire un apercu borne des lignes |
| GET | `/jobs/` | Oui | Lister ses traitements asynchrones |
| GET | `/jobs/{id}/` | Oui | Lire l'etat d'un traitement |
| POST | `/jobs/{id}/retry/` | Oui | Relancer un traitement en echec |

## Authentification

### `GET /auth/csrf/`

Reponse `200` :

```json
{"csrfToken": "jeton-a-envoyer-dans-X-CSRFToken"}
```

### `POST /auth/register/`

Corps JSON :

```json
{
  "username": "marie",
  "email": "marie@example.com",
  "password": "mot-de-passe-solide",
  "password_confirm": "mot-de-passe-solide"
}
```

Reponse `201` : utilisateur cree. Une session est ouverte immediatement.

### `POST /auth/login/`

Corps JSON :

```json
{"username": "marie", "password": "mot-de-passe-solide"}
```

Reponse `200` : utilisateur connecte. Erreur `400` si les identifiants sont invalides.

### `GET /auth/me/`

Reponse `200` : informations publiques du compte connecte. Erreur `403` sans session.

### `POST /auth/logout/`

Reponse `204` sans corps. La session courante est fermee.

## Projets

### `GET /projects/`

Retourne uniquement les projets appartenant a l'utilisateur connecte. Chaque resultat
contient `id`, `name`, `description`, `uploaded_file_count`, `created_at` et `updated_at`.

### `POST /projects/`

Corps JSON :

```json
{"name": "Donnees clients", "description": "Nettoyage des exports CRM"}
```

Reponse `201`. Le champ `name` est obligatoire.

### `GET`, `PUT`, `PATCH /projects/{id}/`

Permet de lire ou modifier son projet. `PATCH` accepte seulement les champs a changer.
Une ressource appartenant a un autre utilisateur est retournee comme introuvable (`404`).

## Imports de fichiers

### `POST /uploads/`

Dans Postman, choisir **Body > form-data** :

| Cle | Type | Obligatoire | Valeur |
|---|---|---|---|
| `project` | Text | Oui | Identifiant numerique du projet |
| `name` | Text | Non | Nom fonctionnel du dataset |
| `file` | File | Oui | Fichier `.csv`, `.json` ou `.xml` |

La taille maximale est `50 Mo` par defaut et peut etre configuree avec
`MAX_UPLOAD_SIZE_MB`. Reponse `201` lorsque le fichier est accepte. Selon sa taille,
le profil est produit immediatement ou confie au worker Celery.

Statuts possibles de l'import : `uploaded`, `validation_pending`, `processing`,
`validated`, `invalid`, `failed`.

### `GET /uploads/` et `GET /uploads/{id}/`

Retournent les metadonnees, les erreurs de validation et le profil du fichier. L'URL
du fichier source peut egalement etre presente dans le champ `file`.

### `GET /uploads/{id}/preview/?limit=20`

Retourne un apercu tabulaire du fichier valide. `limit` vaut 20 par defaut et doit
etre compris entre 1 et 100. Le serveur ne retourne jamais plus de lignes que cette
limite.

```json
{
  "columns": ["name", "score"],
  "rows": [{"name": "Alice", "score": 10}],
  "returned_rows": 1,
  "limit": 20,
  "truncated": false
}
```

Une limite invalide retourne `400`. Un fichier pas encore valide retourne `409`.
Une ressource appartenant a un autre utilisateur retourne `404`.

## Traitements

### `GET /jobs/`

Filtres optionnels :

| Parametre | Exemple | Description |
|---|---|---|
| `status` | `?status=processing` | Filtrer par statut |
| `project` | `?project=3` | Filtrer par projet |
| `upload` | `?upload=12` | Filtrer par fichier importe |

Statuts possibles : `pending`, `processing`, `completed`, `failed`, `cancelled`.
La progression est un entier de `0` a `100`.

### `GET /jobs/{id}/`

Retourne notamment `status`, `progress`, `attempts`, `error_message`, les dates de
debut et de fin, ainsi que les identifiants du projet et du fichier associes.

### `POST /jobs/{id}/retry/`

Relance uniquement un job dont le statut est `failed`. Le job et le fichier repassent
en attente avant l'envoi a Celery. Reponse `202` avec le job mis a jour lorsque la
tache est acceptee. Un autre statut retourne `400`. Si Redis est indisponible, la
reponse est `503` et le job reste `pending` afin d'etre repris ulterieurement.

## Codes d'erreur usuels

| Code | Signification |
|---|---|
| `400` | Donnees invalides ou identifiants incorrects |
| `403` | Session absente ou jeton CSRF invalide |
| `404` | Ressource absente ou appartenant a un autre utilisateur |
| `409` | Etat actuel incompatible avec l'action demandee |
| `413` | Requete trop volumineuse au niveau du serveur mandataire, s'il est configure |
| `503` | Service asynchrone temporairement indisponible |
| `500` | Erreur serveur inattendue |

## Routes planifiees, non disponibles

Les actions d'annulation d'un traitement, les pipelines, les annotations,
les rapports, les exports et l'IA n'ont pas encore de contrat executable. Elles seront
documentees lorsqu'elles seront implementees et testables.
