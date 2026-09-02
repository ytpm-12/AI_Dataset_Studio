# Cahier des charges technique

## Architecture recommandée

- Application : Django full-stack.
- Frontend : Django Templates, CSS, HTMX et Alpine.js en amélioration progressive.
- Traitement data : pandas, puis Polars si les volumes l'exigent.
- Stockage MVP : SQLite et fichiers locaux.
- Tests : pytest, pytest-django et tests de services data.

## Modules Django

- `apps.projects` : gestion des projets dataset.
- `apps.datasets` : import, fichiers et métadonnées.
- `apps.cleaning` : profiling qualité et transformations pandas.
- `apps.annotation` : annotation et validation.
- `apps.exports` : exports standards.

## Routes indicatives

| Route | Méthode | Usage |
|---|---|---|
| `/projects` | POST/GET | Créer et lister les projets |
| `/projects/{id}/upload` | POST | Importer un dataset |
| `/datasets/{id}/profile` | GET | Lire les métriques qualité |
| `/datasets/{id}/clean` | POST | Appliquer une règle |
| `/datasets/{id}/annotations` | GET/POST | Lire et enregistrer les annotations |
| `/datasets/{id}/export` | POST | Exporter un dataset |

## Rôle de pandas

pandas reste le moteur de traitement des données derrière Django. Django orchestre les vues, les formulaires, les fichiers, la base de données et les droits. pandas lit les fichiers, calcule les métriques qualité, détecte les doublons, repère les valeurs manquantes et applique les transformations.

## IA

L'IA n'est pas obligatoire pour le MVP. Elle pourra être ajoutée plus tard comme couche d'assistance pour proposer des règles de nettoyage, expliquer les anomalies ou générer un rapport qualité en langage naturel.
