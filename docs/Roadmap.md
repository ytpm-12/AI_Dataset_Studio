# AI Dataset Studio - Feuille de route incrementale

Derniere mise a jour : 04/11/2026

## Principes de livraison

- Travailler par petits increments demonstrables.
- Toute fonction doit disposer d'une interface ou d'un endpoint testable.
- Tout endpoint doit etre documente dans le contrat d'API et la collection Postman.
- Chaque increment comprend ses tests automatises et une verification manuelle.
- Les transformations sensibles et les recommandations IA restent validables par un humain.

## Architecture officielle

- Frontend cible : React + Vite, execute et gere avec Node.js.
- Backend : Django et Django REST Framework.
- Base de donnees : PostgreSQL.
- Traitements asynchrones : Celery avec Redis comme broker.
- Traitement tabulaire : pandas.
- IA : moteur hybride, regles deterministes puis Qwen3 pour les cas ambigus.

Les templates Django existants constituent un prototype fonctionnel temporaire. Ils
servent de reference pendant la construction progressive du frontend Node.js.

## Phase 1 - Stabiliser l'existant

Etat : en cours

- [x] Mettre en place Django, PostgreSQL, Redis et Celery.
- [x] Implementer l'authentification par session et CSRF.
- [x] Creer les projets et isoler les donnees par utilisateur.
- [x] Importer et profiler les fichiers CSV, JSON et XML.
- [x] Suivre les traitements avec `ProcessingJob`.
- [x] Fournir des interfaces Django minimales.
- [x] Recenser les endpoints dans un contrat API versionne.
- [x] Officialiser le frontend React + Vite sous Node.js.
- [x] Fournir une collection Postman reproductible.
- [x] Confirmer la connexion Django a PostgreSQL.
- [ ] Retablir Docker Desktop et confirmer Redis (`PONG`).
- [ ] Demarrer et confirmer le worker Celery apres Redis.
- [x] Executer et valider les 29 tests automatises avec PostgreSQL.

Critere de sortie : infrastructure verte, 29 tests reussis et parcours Postman
authentification -> projet -> upload -> traitement reproductible.

## Phase 2 - Terminer le parcours d'import

Etat : en cours

- [x] Creer le frontend Node.js et son socle de navigation.
- [x] Configurer le proxy Vite, les cookies de session et les origines CSRF locales.
- [ ] Definir les origines et la strategie de deploiement du frontend en production.
- [x] Migrer login, inscription, projets et upload vers React.
- [x] Afficher le detail d'un dataset et un apercu borne de ses lignes.
- [x] Afficher le detail, le profil des colonnes et les erreurs de validation.
- [x] Actualiser le statut d'un traitement depuis le frontend.
- [x] Permettre la relance controlee d'un traitement echoue.

Critere de sortie : un utilisateur importe un fichier et consulte son profil complet
sans utiliser l'administration Django.

## Phase 3 - Nettoyage et historique

- [ ] Detecter et traiter les doublons.
- [ ] Traiter les valeurs manquantes.
- [ ] Convertir les types et normaliser les formats.
- [ ] Previsualiser chaque transformation avant application.
- [ ] Conserver l'historique et permettre l'annulation logique.
- [ ] Ajouter API, interface et tests a chaque regle.

Critere de sortie : un dataset peut etre nettoye de maniere explicable et reversible.

## Phase 4 - Annotation et qualite

- [ ] Definir les schemas et campagnes d'annotation.
- [ ] Annoter et valider des enregistrements.
- [ ] Calculer un score de qualite.
- [ ] Analyser la distribution et l'equilibre des classes.
- [ ] Organiser la validation humaine.

## Phase 5 - Export et rapports

- [ ] Exporter en CSV et JSON.
- [ ] Generer un rapport qualite.
- [ ] Consulter et telecharger l'historique des resultats.
- [ ] Tester les exports sur des volumes representatifs.

## Phase 6 - Integration IA

- [ ] Integrer les regles deterministes de `ai_lab` dans `apps.ai_engine`.
- [ ] Appeler Qwen3 uniquement pour les cas ambigus ou non couverts.
- [ ] Valider les sorties avec le schema JSON du projet.
- [ ] Afficher les recommandations et leur justification.
- [ ] Exiger une confirmation humaine avant transformation.
- [ ] Reevaluer le LoRA sur des cas reels valides.

## Phase 7 - Livraison MVP

- [ ] Tests de bout en bout frontend/backend/worker.
- [ ] Revue de securite, performances et limites d'upload.
- [ ] Documentation d'installation, exploitation et utilisation.
- [ ] Environnement de demonstration reproductible.
- [ ] Presentation et livraison du MVP.
