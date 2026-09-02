# Plan de presentation - Maquette AI Dataset Studio

Objectif de la presentation: mettre tous les collaborateurs au meme niveau de comprehension sur l'architecture UI/UX, les ecrans, les composants et les capacites de la plateforme.

Durée conseillee: 35 a 45 minutes  
Public: equipe projet, developpeurs, encadrants, collaborateurs fonctionnels, futurs utilisateurs pilotes  
Support: ouvrir `docs/04_Design/ui-mockup/index.html` et utiliser les captures dans `docs/04_Design/ui-mockup/screenshots`

---

## 1. Ouverture - 3 minutes

### Message cle

AI Dataset Studio est un studio de preparation de datasets IA: importer, analyser, nettoyer, annoter, equilibrer, valider et exporter.

### A montrer

![Tableau de bord](ui-mockup/screenshots/01-dashboard.png)

### Script oral

"Cette maquette montre la plateforme comme un outil de production. L'utilisateur ne manipule pas seulement des fichiers: il suit un dataset dans un pipeline controle, avec des versions, des traitements et des decisions humaines."

---

## 2. Positionnement produit et direction visuelle - 4 minutes

### Points a expliquer

- Positionnement "Canva des datasets IA".
- Interface claire et guidee, mais rigoureuse.
- Rail sombre pour le cote application de travail.
- Fond papier pour lisibilite et calme.
- Teal pour controle et fiabilite.
- Ambre pour avertissements et validation humaine.
- Rouge pour anomalies.
- Violet pour IA.

### Image

![Dashboard](ui-mockup/screenshots/01-dashboard.png)

### Message a retenir

La maquette cherche l'equilibre entre accessibilite et precision technique.

---

## 3. Architecture de navigation - 4 minutes

### Points a expliquer

- Navigation decoupee en trois zones:
  - Workspace;
  - Pipeline;
  - Resultats.
- Chaque ecran correspond a une etape ou une decision.
- Le projet actif reste visible en permanence.

### Image

![Version active](ui-mockup/screenshots/03-project.png)

### Qui fait quoi?

Utilisateur:

- navigue;
- choisit le projet;
- valide les actions.

Systeme:

- conserve le contexte actif;
- affiche version, statut et progression.

---

## 4. Projet dataset et versionnement - 5 minutes

### Ecrans a montrer

![Projets](ui-mockup/screenshots/02-projects.png)

![Version active](ui-mockup/screenshots/03-project.png)

### Points a expliquer

- Un projet dataset contient des datasets, versions, transformations, rapports et exports.
- La source importee est immuable.
- Chaque transformation importante produit une version ou un evenement trace.
- Le thread de version est le motif visuel qui rend cette logique visible.

### Message a retenir

La plateforme evite les modifications silencieuses.

---

## 5. Import et validation de source - 4 minutes

### Image

![Import](ui-mockup/screenshots/04-import.png)

### Points a expliquer

- L'import n'est pas seulement un upload.
- Formats prevus: CSV, JSON, XML, PDF, images.
- Verification format, structure, encodage.
- Apercu schema.
- Gestion d'erreurs explicite.

### Qui fait quoi?

Utilisateur:

- depose ou selectionne un fichier;
- valide la structure.

Systeme:

- detecte format;
- lit schema;
- signale erreurs;
- cree la premiere version exploitable.

---

## 6. Analyse et profilage - 4 minutes

### Image

![Analyse](ui-mockup/screenshots/05-profiling.png)

### Points a expliquer

- Le profilage rend la qualite visible.
- Metriques principales: colonnes, doublons, outliers, completude.
- Visualisations: distribution, heatmap de valeurs manquantes, tableau colonnes.
- Les recommandations commencent ici.

### Message a retenir

Avant de nettoyer, on comprend.

---

## 7. Nettoyage et transformation - 4 minutes

### Image

![Nettoyage](ui-mockup/screenshots/06-cleaning.png)

### Points a expliquer

- Les regles sont ordonnees.
- La preview avant/apres rend l'impact visible.
- Les recommandations IA sont explicables.
- L'application cree une version candidate.

### Qui fait quoi?

Utilisateur:

- choisit les regles;
- accepte ou rejette;
- applique.

Systeme:

- estime l'impact;
- execute le traitement;
- historise.

IA:

- propose;
- explique;
- attend validation.

---

## 8. Donnees non tabulaires: PDF et images - 5 minutes

### Images

![Documents PDF](ui-mockup/screenshots/07-documents.png)

![Images](ui-mockup/screenshots/08-images.png)

### Points a expliquer

PDF:

- OCR;
- extraction texte;
- reconstruction de tableaux;
- detection d'erreurs documentaires.

Images:

- resolution;
- flou;
- corruption;
- doublons visuels;
- coherence des labels.

### Message a retenir

AI Dataset Studio n'est pas limite au CSV: il prepare aussi les sources documentaires et visuelles.

---

## 9. Annotation et validation humaine - 4 minutes

### Image

![Annotation](ui-mockup/screenshots/09-annotation.png)

### Points a expliquer

- File d'elements a annoter.
- Zone centrale de lecture ou inspection.
- Palette de labels.
- Suggestion IA avec confiance.
- Decision humaine obligatoire.

### Message a retenir

L'IA assiste, mais l'humain garde le controle.

---

## 10. Recommandations IA - 4 minutes

### Image

![Recommandations IA](ui-mockup/screenshots/10-ai.png)

### Points a expliquer

- Une recommandation IA est structuree:
  - type;
  - cible;
  - action proposee;
  - confiance;
  - statut.
- Elle peut etre acceptee ou rejetee.
- Elle est historisee.

### Message a retenir

La plateforme traite l'IA comme un moteur de suggestion auditable.

---

## 11. Equilibrage - 3 minutes

### Image

![Equilibrage](ui-mockup/screenshots/11-balancing.png)

### Points a expliquer

- Comparaison distribution actuelle / distribution cible.
- Choix d'une strategie.
- Estimation de l'impact.
- Creation d'une version candidate.

### Message a retenir

L'equilibrage est une decision de preparation, pas une operation cachee.

---

## 12. Rapport qualite et export - 5 minutes

### Images

![Rapport qualité](ui-mockup/screenshots/12-report.png)

![Export](ui-mockup/screenshots/13-export.png)

### Points a expliquer

Rapport:

- score global;
- decision;
- sections OK / WARN;
- journal des operations.

Export:

- formats CSV, JSON, COCO, YOLO, Hugging Face;
- dataset prepare;
- annotations;
- pipeline JSON;
- rapport qualite;
- manifest.

### Message a retenir

Le dataset exporte n'est pas seulement un fichier: c'est un paquet documente et tracable.

---

## 13. Suivi des traitements - 3 minutes

### Image

![Traitements](ui-mockup/screenshots/14-jobs.png)

### Points a expliquer

- Les traitements longs sont des jobs.
- Etats affiches:
  - `QUEUED`;
  - `RUNNING`;
  - `SUCCEEDED`;
  - `SUCCEEDED_WITH_WARNINGS`;
  - `FAILED`.
- L'utilisateur peut suivre, ouvrir details ou annuler.

### Message a retenir

L'interface reste non bloquante et transparente.

---

## 14. Composants UI a normaliser - 4 minutes

### Liste a presenter

- Rail lateral;
- topbar;
- page header;
- carte metrique;
- chip de statut;
- progress bar;
- tableau de donnees;
- thread de version;
- dropzone;
- split preview;
- panel de recommandation IA;
- donut score;
- heatmap;
- modale;
- toast.

### Decision attendue de l'equipe

Valider ces composants comme base du design system MVP.

---

## 15. Questions a poser aux collaborateurs - 5 minutes

Questions fonctionnelles:

1. Les etapes du pipeline sont-elles completes pour le MVP?
2. Les termes utilises sont-ils clairs pour un utilisateur non expert?
3. Le mode manuel / assiste / automatique est-il assez visible?
4. Les warnings sont-ils suffisamment differencies des erreurs?
5. L'IA est-elle presente au bon niveau, sans donner l'impression qu'elle agit seule?

Questions techniques:

1. Veut-on implementer en Django Templates + HTMX ou React + TypeScript?
2. Quels composants doivent devenir reutilisables en premier?
3. Quels ecrans doivent etre connectes au backend en priorite?
4. Quelle structure API correspond a chaque ecran?
5. Quels jobs doivent etre visibles dans la premiere demo?

Questions UX:

1. Le dashboard donne-t-il assez vite l'etat du projet?
2. L'import est-il assez rassurant?
3. Le rapport qualite permet-il vraiment de decider?
4. L'annotation est-elle assez rapide pour un usage quotidien?
5. Les ecrans PDF/images sont-ils comprehensibles pour les utilisateurs cibles?

---

## 16. Conclusion proposee - 2 minutes

Script:

"Cette maquette pose la premiere version de l'experience AI Dataset Studio. Elle montre comment rendre la preparation de datasets visuelle, guidee et tracable. Le point central est la confiance: confiance dans les versions, dans les traitements, dans les recommandations IA et dans l'export final. La prochaine etape est de valider ces ecrans avec l'equipe, puis de transformer les composants en implementation MVP."

---

## 17. Ordre de demonstration rapide

Si le temps est court, montrer seulement:

1. Dashboard
2. Version active
3. Import
4. Analyse
5. Nettoyage
6. Annotation
7. Rapport qualite
8. Export
9. Jobs

Durée: 15 a 20 minutes.

