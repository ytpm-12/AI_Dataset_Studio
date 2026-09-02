# Rapport UI/UX - Maquette AI Dataset Studio

Date: 19 aout 2026  
Objet: expliquer la maquette HTML/CSS/JavaScript produite pour AI Dataset Studio, ses ecrans, composants, intentions UX et logique fonctionnelle.  
Chemin de la maquette: `docs/04_Design/ui-mockup/index.html`

---

## 1. Resume executif

La maquette represente AI Dataset Studio comme un **studio de preparation de datasets IA**, pense comme un outil de travail quotidien pour data scientists, chercheurs, et equipes IA. L'interface ne se limite pas a afficher des tables: elle rend visible tout le cycle de vie d'un dataset, depuis l'import jusqu'a l'export, avec:

- une navigation par pipeline;
- un suivi clair des versions;
- une separation entre actions humaines, traitements systeme et recommandations IA;
- des indicateurs qualite lisibles;
- des etats de jobs compatibles avec les specifications techniques;
- des ecrans dedies aux donnees tabulaires, PDF, images, annotation, equilibrage et export.

L'intention principale est de traduire le positionnement **"Canva des datasets IA"** en experience produit: simple, visuelle, guidee, mais suffisamment rigoureuse pour respecter la tracabilite, l'immutabilite des sources et la validation humaine.

![Tableau de bord](ui-mockup/screenshots/01-dashboard.png)

---

## 2. Intention de design

### 2.1 Identite visuelle

La direction graphique retenue est celle d'un **instrument de laboratoire pour la donnee**:

- fond papier clair pour la lisibilite;
- rail lateral sombre pour donner une sensation d'application professionnelle;
- accent principal vert pin / teal pour evoquer controle, precision et fiabilite;
- accent ambre pour les avertissements, validations humaines et recommandations;
- rouge brique limite aux anomalies ou erreurs critiques;
- violet reserve aux suggestions IA afin de distinguer ce qui vient du moteur d'assistance.

Le but n'est pas d'avoir une interface spectaculaire, mais une interface **calme, dense, lisible et rassurante**.

### 2.2 Motif signature: le thread de version

Le motif distinctif de la maquette est le **thread de version**: une ligne verticale pointillee qui relie les versions, les actions et les evenements.

Ce motif rappelle une idee fondamentale du projet: **rien n'est ecrase silencieusement**. Chaque transformation significative produit ou documente un nouvel etat.

Il apparait notamment dans:

- le tableau de bord;
- la page version active;
- le rapport qualite;
- le journal des traitements.

### 2.3 Principes UX

La maquette suit cinq principes:

1. **Toujours montrer ou l'utilisateur se trouve**: rail lateral, fil d'Ariane, titre de page.
2. **Faire comprendre l'etat du dataset en un coup d'oeil**: score qualite, anomalies, valeurs manquantes, jobs actifs.
3. **Ne jamais masquer les traitements longs**: chaque traitement est represente comme job.
4. **Distinguer humain, systeme et IA**: boutons, statuts, recommandations, validations.
5. **Previsualiser avant d'appliquer**: nettoyage, equilibrage et export sont presentes comme decisions controlees.

---

## 3. Architecture de la maquette produite

La maquette est une application front autonome:

| Fichier | Role |
|---|---|
| `index.html` | Point d'entree de la maquette. Charge le CSS et le JavaScript. |
| `styles.css` | Design system, tokens couleurs, layout, composants UI, responsive. |
| `app.js` | Navigation, rendu des ecrans, interactions simples, toasts et modale. |
| `capture-screenshots.js` | Script Playwright pour generer les captures des ecrans. |
| `screenshots/*.png` | Images de reference integrees dans ce rapport. |

La navigation fonctionne par hash routes:

- `#dashboard`
- `#projects`
- `#project`
- `#import`
- `#profiling`
- `#cleaning`
- `#documents`
- `#images`
- `#annotation`
- `#ai`
- `#balancing`
- `#report`
- `#export`
- `#jobs`

Cette structure permet de parcourir la maquette sans backend. Plus tard, elle pourra etre transformee:

- soit en templates Django + HTMX;
- soit en application React + TypeScript;
- soit en base de specification UI pour Figma.

---

## 4. Qui fait quoi dans la plateforme?

### 4.1 Utilisateur / Owner

L'utilisateur principal est celui qui:

- cree un projet dataset;
- importe des fichiers;
- choisit le mode manuel, assiste ou automatique;
- valide ou rejette les recommandations IA;
- applique des regles de nettoyage;
- annote les donnees;
- controle le score qualite;
- exporte une version.

Dans la maquette, il est represente par l'espace utilisateur `Prince Migwel - Owner`.

### 4.2 Moteur de traitement

Le moteur de traitement:

- lit les fichiers;
- detecte schema, types, colonnes et erreurs;
- calcule les metriques qualite;
- detecte doublons, valeurs manquantes et anomalies;
- applique les transformations validees;
- produit de nouvelles versions.

Il est visualise dans l'interface par:

- les barres de progression;
- les jobs;
- les statuts `RUNNING`, `QUEUED`, `SUCCEEDED`, `FAILED`;
- les scores apres traitement.

### 4.3 Moteur IA

Le moteur IA n'agit pas comme une boite noire autonome. Dans la maquette, il:

- propose des regles de nettoyage;
- explique pourquoi une action est recommandee;
- pre-annote des donnees;
- signale des anomalies avancees;
- donne un niveau de confiance;
- attend une decision humaine.

Les elements IA utilisent un ton violet ou ambre, et des libelles comme `PENDING_USER_DECISION`.

### 4.4 Workers specialises

La maquette materialise plusieurs workers:

- worker data: CSV, JSON, XML, profilage, nettoyage;
- worker PDF/OCR: extraction texte, tableaux, mise en page;
- worker image: resolution, flou, doublons visuels, labels;
- worker IA: recommandations, pre-annotation, explication;
- worker export: generation des formats de sortie.

### 4.5 Systeme de versionnement

Le systeme garantit:

- source conservee en lecture seule;
- transformation historisee;
- version candidate avant export;
- retour possible vers une version precedente;
- journalisation visible dans le rapport.

---

## 5. Composants UI principaux

### 5.1 Rail lateral

Le rail lateral est la colonne sombre a gauche. Il structure toute l'application.

Fonctions:

- acces aux pages workspace;
- acces aux etapes pipeline;
- acces aux resultats;
- affichage du projet actif;
- acces au profil utilisateur.

Subtilite UX: le rail montre que la plateforme est un **outil de production**, pas une landing page. L'utilisateur garde en permanence une vision du parcours complet.

### 5.2 Topbar

La barre superieure contient:

- bouton menu mobile;
- fil d'Ariane;
- recherche globale;
- notifications;
- parametres.

Subtilite UX: la recherche globale prepare une future experience de navigation rapide dans projets, versions, colonnes et jobs.

### 5.3 Page header

Chaque page commence par:

- un eyebrow indiquant le contexte;
- un titre clair;
- une description courte;
- des actions principales.

Subtilite UX: cela aide chaque collaborateur a comprendre le role de l'ecran sans documentation externe.

### 5.4 Cartes metriques

Les cartes metriques affichent:

- score qualite;
- valeurs manquantes;
- anomalies;
- annotations;
- projets;
- versions;
- exports.

Subtilite UX: les chiffres importants sont grands, les details sont en chips colores.

### 5.5 Status chips

Les chips de statut distinguent:

- succes: vert;
- avertissement: ambre;
- erreur: rouge;
- traitement en cours: bleu;
- IA / decision: violet ou ambre.

Subtilite UX: les statuts sont visibles sans lire toute la ligne.

### 5.6 Progress bars

Les barres de progression servent pour:

- jobs;
- controles qualite;
- import;
- extraction PDF;
- equilibrage;
- compatibilite export.

Subtilite UX: elles reduisent l'anxiete autour des traitements longs.

### 5.7 Tableaux

Les tableaux sont utilises pour:

- liste de projets;
- profil colonnes;
- apercu schema;
- issues image.

Subtilite UX: ils sont denses, mais encadres par des titres et statuts pour rester lisibles.

### 5.8 Dropzone

La dropzone d'import montre:

- formats acceptes;
- taille maximale configuree;
- action de validation;
- controle de structure.

Subtilite UX: l'import est traite comme une phase de validation, pas comme un simple upload.

### 5.9 Split preview avant/apres

La page nettoyage utilise une comparaison avant/apres.

Fonction:

- montrer l'effet d'une regle;
- eviter les modifications silencieuses;
- rendre l'utilisateur responsable de la validation.

### 5.10 Modale de creation projet

La modale permet de creer un projet dataset avec:

- nom;
- type principal;
- objectif.

Subtilite UX: le projet commence par une intention, pas seulement par un fichier.

### 5.11 Toasts

Les toasts confirment:

- creation projet;
- validation;
- action IA;
- export;
- actualisation jobs.

Subtilite UX: les retours sont courts et actionnables.

---

## 6. Inventaire detaille des ecrans

### 6.1 Tableau de bord

Objectif: donner une vision instantanee du workspace actif.

Ce que l'utilisateur voit:

- positionnement produit;
- job en cours;
- mini pipeline;
- metriques principales;
- thread de version;
- jobs actifs.

Ce que l'utilisateur peut faire:

- ouvrir le projet actif;
- surveiller les jobs;
- comprendre le niveau de qualite actuel.

Subtilite UI/UX:

- le hero sombre donne un point d'entree fort;
- le thread de version met en avant la tracabilite;
- les jobs actifs rassurent sur les traitements asynchrones.

![Tableau de bord](ui-mockup/screenshots/01-dashboard.png)

### 6.2 Projets dataset

Objectif: gerer tous les projets de preparation.

Ce que l'utilisateur voit:

- nombre de projets;
- nombre de versions;
- elements a verifier;
- exports disponibles;
- tableau des projets.

Ce que l'utilisateur peut faire:

- creer un projet;
- filtrer les projets;
- ouvrir un projet.

Ce que le systeme montre:

- type de dataset;
- volume;
- version active;
- score qualite;
- etat courant.

![Projets](ui-mockup/screenshots/02-projects.png)

### 6.3 Version active

Objectif: presenter le projet courant comme un pipeline versionne.

Ce que l'utilisateur voit:

- etapes du pipeline;
- mode de controle;
- versions existantes;
- objets techniques principaux.

Ce que l'utilisateur peut faire:

- aller vers import;
- consulter rapport;
- changer mentalement de mode manuel / assiste / auto.

Subtilite UI/UX:

- cette page relie la vision metier aux objets techniques: projet, dataset, version, job, transformation, recommendation.

![Version active](ui-mockup/screenshots/03-project.png)

### 6.4 Import et validation

Objectif: importer une source sans la modifier et valider sa structure.

Ce que l'utilisateur voit:

- zone de depot;
- formats acceptes;
- controles format / structure / encodage;
- apercu schema;
- erreurs possibles.

Ce que l'utilisateur peut faire:

- deposer un fichier;
- valider la structure;
- identifier les colonnes a confirmer.

Ce que le systeme fait:

- verifie format;
- detecte schema;
- signale erreurs d'import;
- prepare la premiere version exploitable.

![Import](ui-mockup/screenshots/04-import.png)

### 6.5 Analyse et profilage

Objectif: evaluer la qualite du dataset avant transformation.

Ce que l'utilisateur voit:

- nombre de colonnes;
- doublons;
- outliers;
- completude;
- distribution des classes;
- carte de valeurs manquantes;
- profil colonne par colonne.

Ce que le systeme fait:

- calcule statistiques;
- detecte anomalies;
- propose recommandations.

Subtilite UI/UX:

- les visualisations donnent une lecture rapide avant d'entrer dans les details.

![Analyse](ui-mockup/screenshots/05-profiling.png)

### 6.6 Nettoyage et transformation

Objectif: appliquer des transformations explicites et tracables.

Ce que l'utilisateur voit:

- liste de regles ordonnees;
- preview avant/apres;
- impact estime;
- explication IA.

Ce que l'utilisateur peut faire:

- ajouter une regle;
- accepter une recommandation;
- appliquer les transformations.

Ce que le systeme fait:

- calcule l'impact;
- cree une version candidate;
- conserve la trace de l'operation.

![Nettoyage](ui-mockup/screenshots/06-cleaning.png)

### 6.7 Documents PDF

Objectif: traiter des documents PDF comme sources de dataset.

Ce que l'utilisateur voit:

- liste des pages;
- rendu document simplifie;
- indicateurs OCR, tableaux et mise en page;
- erreurs documentaires.

Ce que le systeme fait:

- extrait texte;
- detecte tableaux;
- evalue confiance OCR;
- signale les extractions partielles.

Subtilite UI/UX:

- le PDF est traite comme un objet visuel et structurel, pas uniquement comme du texte brut.

![Documents PDF](ui-mockup/screenshots/07-documents.png)

### 6.8 Images

Objectif: controler la qualite d'un corpus image.

Ce que l'utilisateur voit:

- grille d'echantillons;
- images floues ou suspectes;
- controles resolution, flou, similarite, labels;
- tableau des issues.

Ce que le systeme fait:

- detecte images corrompues ou floues;
- repere doublons visuels;
- signale labels incoherents.

![Images](ui-mockup/screenshots/08-images.png)

### 6.9 Annotation

Objectif: valider humainement les labels.

Ce que l'utilisateur voit:

- file d'enregistrements;
- contenu a annoter;
- labels disponibles;
- suggestion IA avec confiance et explication.

Ce que l'utilisateur peut faire:

- accepter une pre-annotation;
- corriger un label;
- valider l'annotation.

Ce que l'IA fait:

- propose un label;
- explique la proposition;
- attend validation humaine.

![Annotation](ui-mockup/screenshots/09-annotation.png)

### 6.10 Recommandations IA

Objectif: centraliser les propositions IA et decisions humaines.

Ce que l'utilisateur voit:

- type de recommandation;
- cible;
- action proposee;
- confiance;
- statut de decision.

Ce que l'utilisateur peut faire:

- accepter;
- rejeter;
- demander de nouvelles recommandations.

Subtilite UI/UX:

- la recommandation IA est une entite auditable, pas une action magique.

![Recommandations IA](ui-mockup/screenshots/10-ai.png)

### 6.11 Equilibrage

Objectif: analyser et corriger le desequilibre des classes.

Ce que l'utilisateur voit:

- distribution avant;
- distribution cible;
- strategie proposee;
- impact estime.

Ce que l'utilisateur peut faire:

- choisir methode;
- choisir colonne cible;
- configurer seuil;
- appliquer strategie.

Ce que le systeme fait:

- calcule pertes;
- estime gain de balance;
- cree version candidate.

![Equilibrage](ui-mockup/screenshots/11-balancing.png)

### 6.12 Rapport qualite

Objectif: synthetiser l'etat final d'une version.

Ce que l'utilisateur voit:

- score global;
- decision de validation;
- sections du rapport;
- journal des operations.

Ce que l'utilisateur peut faire:

- generer le rapport;
- exporter en PDF;
- verifier les warnings avant export.

Subtilite UI/UX:

- le rapport n'est pas seulement une sortie: c'est un ecran de decision.

![Rapport qualite](ui-mockup/screenshots/12-report.png)

### 6.13 Export

Objectif: exporter la version preparee vers des formats standards.

Ce que l'utilisateur voit:

- formats CSV, JSON, COCO, YOLO, Hugging Face;
- contenu inclus dans le paquet;
- manifest export;
- compatibilite.

Ce que l'utilisateur peut faire:

- choisir format;
- exporter;
- verifier les metadonnees incluses.

Ce que le systeme fait:

- empaquete data, annotations, pipeline et rapport;
- signale les warnings;
- conserve l'export comme artefact.

![Export](ui-mockup/screenshots/13-export.png)

### 6.14 Traitements

Objectif: suivre les jobs longs.

Ce que l'utilisateur voit:

- identifiant job;
- nom du traitement;
- progression;
- statut;
- action detail ou annulation.

Etats representes:

- `QUEUED`
- `RUNNING`
- `SUCCEEDED`
- `SUCCEEDED_WITH_WARNINGS`
- `FAILED`

Subtilite UI/UX:

- les traitements longs ne bloquent pas l'interface; ils deviennent des objets suivables.

![Traitements](ui-mockup/screenshots/14-jobs.png)

---

## 7. Logique de navigation

Le parcours recommande pour une demonstration est:

1. Tableau de bord: comprendre le studio.
2. Projets: choisir ou creer un projet.
3. Version active: voir pipeline et versionnement.
4. Import: charger et valider source.
5. Analyse: diagnostiquer qualite.
6. Nettoyage: appliquer regles.
7. Annotation: valider humainement.
8. Recommandations IA: comprendre l'assistance.
9. Equilibrage: corriger classes.
10. Rapport: decider si la version est prete.
11. Export: livrer le dataset.
12. Traitements: surveiller workers.

---

## 8. Ce que la maquette couvre deja

La maquette couvre les exigences UI/UX suivantes:

- creation de projet dataset;
- import multi-format;
- validation de structure;
- profilage qualite;
- nettoyage avec preview;
- traitement PDF;
- traitement image;
- annotation et pre-annotation;
- recommandations IA explicables;
- equilibrage;
- rapport qualite;
- export multi-format;
- suivi des traitements longs;
- thread de version;
- modes manuel / assiste / automatique;
- distinction des statuts metier et techniques.

---

## 9. Limites actuelles de la maquette

La maquette est volontairement front-only:

- pas de backend Django connecte;
- pas de vraie lecture fichier;
- pas de vraie base de donnees;
- pas de service IA;
- pas de persistance locale;
- donnees exemples statiques;
- interactions limitees a navigation, modale, toasts, boutons et segments.

Ces limites sont normales pour une maquette UI/UX. Le but est de figer l'experience, les ecrans, les composants et la logique de presentation avant implementation.

---

## 10. Recommandations pour la suite

Priorites proposees:

1. Valider le vocabulaire fonctionnel avec toute l'equipe.
2. Choisir la stack front finale: Django Templates + HTMX ou React + TypeScript.
3. Transformer les composants recurrents en design system.
4. Produire les maquettes mobile des ecrans principaux.
5. Definir les contrats API reels pour chaque ecran.
6. Brancher l'import CSV/JSON sur un premier backend.
7. Connecter le profilage pandas.
8. Ajouter les etats reels des jobs.
9. Migrer la direction visuelle vers Figma si besoin de collaboration design.

---

## 11. Glossaire rapide

| Terme | Definition UI/UX |
|---|---|
| Projet dataset | Espace de travail contenant datasets, versions, pipeline et exports. |
| Dataset | Source ou jeu de donnees exploitable. |
| Version | Etat historise du dataset apres import ou transformation. |
| Pipeline | Suite ordonnee d'etapes de preparation. |
| Job | Traitement long execute en arriere-plan. |
| Recommandation IA | Proposition explicable, avec cible, confiance et decision humaine. |
| Rapport qualite | Synthese decisionnelle d'une version. |
| Export | Paquet final pret pour entrainement ou partage. |

