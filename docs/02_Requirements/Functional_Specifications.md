# Cahier des charges fonctionnel

Derniere mise a jour : 04/11/2026

## Vision

AI Dataset Studio permet a un utilisateur de transformer des fichiers bruts en jeux
de donnees propres, documentes, validables et exportables. Chaque etape doit etre
visible, explicable et testable.

## Parcours cible

1. Creer un compte et ouvrir une session.
2. Creer un projet dataset.
3. Importer un fichier CSV, JSON ou XML.
4. Consulter l'apercu, le profil et les erreurs de validation.
5. Previsualiser puis appliquer des regles de nettoyage.
6. Annoter et valider les donnees.
7. Consulter les indicateurs de qualite et d'equilibre.
8. Recevoir des recommandations explicables de l'assistant IA.
9. Exporter le dataset et son rapport.

## Exigences MVP

| ID | Fonction | Priorite | Etat au 04/11/2026 |
|---|---|---|---|
| F-001 | S'inscrire, se connecter et se deconnecter | Must | realise |
| F-002 | Creer et consulter ses projets | Must | realise |
| F-003 | Importer CSV, JSON et XML | Must | realise |
| F-004 | Profiler un dataset | Must | backend realise, interface a completer |
| F-005 | Suivre les traitements volumineux | Must | backend realise, interface a completer |
| F-006 | Previsualiser les lignes du dataset | Must | realise |
| F-007 | Nettoyer les doublons | Must | a faire |
| F-008 | Traiter les valeurs manquantes | Must | a faire |
| F-009 | Convertir les types et formats | Must | a faire |
| F-010 | Previsualiser et confirmer une transformation | Must | a faire |
| F-011 | Annoter et valider des enregistrements | Should | a faire |
| F-012 | Evaluer la qualite et l'equilibre | Should | a faire |
| F-013 | Exporter CSV et JSON | Must | a faire |
| F-014 | Consulter l'historique | Should | a faire |
| F-015 | Recevoir une recommandation IA explicable | Should | laboratoire realise, integration a faire |

## Regles fonctionnelles

- Un utilisateur ne voit et ne modifie que ses propres ressources.
- Un upload appartient obligatoirement a un projet.
- Seuls CSV, JSON et XML sont acceptes dans l'increment actuel.
- Un fichier invalide est conserve avec un statut et des erreurs consultables.
- Un traitement long passe par la file asynchrone.
- Une transformation doit etre previsualisee avant confirmation.
- Une recommandation IA n'applique jamais automatiquement une transformation sensible.

## Interfaces attendues

Chaque fonction livree doit posseder au moins l'un des moyens de verification suivants :

- un ecran React conforme a la charte UI/UX ;
- un endpoint documente et testable dans Postman.

Pendant la migration, les ecrans Django existants restent disponibles comme prototype.

## Criteres d'acceptation transversaux

- Les erreurs sont comprehensibles et n'exposent pas de details internes.
- Les actions longues affichent un statut et une progression.
- Les formulaires sont utilisables sur ordinateur et mobile.
- Chaque endpoint est present dans le contrat API.
- Chaque increment important possede des tests automatises.
