# Rapport final - capacite reelle du moteur IA

Date : 2026-08-29

## Objectif du test

Verifier le comportement reel du moteur AI Dataset Studio sans correction manuelle :

- donnees de reference utilisees pour construire le systeme;
- split de test garde a part;
- CSV reels telecharges en ligne;
- gros volume sur le fichier `eco-counter-data.csv`;
- mode zero-shot, sans few-shot;
- regles deterministes;
- `system_prompt.txt`;
- Qwen3 via Ollama pour comparer les sorties LLM aux regles.

Important : tester sur les donnees d'entrainement ne suffit pas pour prouver la capacite du modele. C'est utile comme controle technique, mais le jugement principal doit venir du split `test` et des CSV reels.

## Donnees testees

| Source | Fichier | Volume |
| --- | --- | ---: |
| Projet | `ai_lab/data/dataset_ventes_sale.csv` | 1 008 lignes |
| Open data | `D:\Downloads\jeu de donnee\eco-counter-data.csv` | 165 994 lignes |
| Open data | `D:\Downloads\jeu de donnee\elecdom_courbes_horaires_detail_appareils.csv` | 624 lignes |
| Benchmark | `cases_train.jsonl` | 125 cas |
| Benchmark | `cases_validation.jsonl` | 27 cas |
| Benchmark | `cases_test.jsonl` | 28 cas |

## Resultats sur cas supervises

Evaluation avec les regles deterministes :

| Split | Cas | Exact | Action | Validation | Duree |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 125 | 100 % | 100 % | 100 % | 0.00s |
| Validation | 27 | 100 % | 100 % | 100 % | 0.00s |
| Test | 28 | 100 % | 100 % | 100 % | 0.00s |

Lecture : les regles couvrent tres bien le perimetre actuellement defini. Le score `train` est attendu et ne doit pas etre surestime; le score `test` est le plus interessant.

## Resultats sur CSV reels

| Fichier | Lignes lues | Colonnes | Profils evalues | Recommandations principales |
| --- | ---: | ---: | ---: | --- |
| `dataset_ventes_sale.csv` | 1 008 | 9 | 10 | valeurs manquantes, outliers, normalisation texte, dates |
| `eco-counter-data.csv` | 165 994 | 9 | 10 | dates, valeurs manquantes, outliers |
| `elecdom_courbes_horaires_detail_appareils.csv` | 624 | 7 | 8 | nombre francais en texte vers `float` |

Actions produites par les regles :

| Fichier | Distribution des actions |
| --- | --- |
| `dataset_ventes_sale.csv` | `no_action`: 2, `review_outliers`: 2, `normalize_text`: 2, `impute_missing`: 3, `standardize_format`: 1 |
| `eco-counter-data.csv` | `no_action`: 1, `standardize_format`: 2, `impute_missing`: 6, `review_outliers`: 1 |
| `elecdom_courbes_horaires_detail_appareils.csv` | `no_action`: 7, `cast_type`: 1 |

## Comparaison Qwen3/Ollama vs regles

Qwen3 a ete teste sur les profils CSV reels en zero-shot, sans few-shot. Le LoRA Kaggle `checkpoint-48` n'est pas encore fusionne dans Ollama localement; ce test mesure donc Qwen3 local + `system_prompt.txt`, puis compare ses sorties aux regles.

| Fichier | Profils testes | Desaccords Qwen/regles | Erreurs contrat/serveur | Duree |
| --- | ---: | ---: | ---: | ---: |
| `dataset_ventes_sale.csv` | 10 | 3 | 2 | 150.65s |
| `eco-counter-data.csv` | 10 | 2 | 0 | 118.22s |
| `elecdom_courbes_horaires_detail_appareils.csv` | 8 | 3 | 0 | 85.23s |
| Total | 28 | 8 | 2 | 354.10s |

Désaccords notables :

- Qwen propose parfois une action au niveau `dataset` alors que la decision doit etre faite par colonne.
- Qwen peut ignorer la priorite des valeurs manquantes et choisir les outliers a la place.
- Qwen propose parfois des normalisations texte non justifiees par les statistiques.
- Deux appels ont echoue cote Ollama/CUDA ou generation JSON.

## Conclusion

Le test confirme que le moteur hybride est la bonne strategie :

```text
profilage pandas -> regles deterministes -> Qwen/LoRA en complement -> validation JSON -> validation humaine
```

Qwen3 est utile pour enrichir les explications et traiter certains cas ambigus, mais il n'est pas assez stable pour decider seul. Les regles deterministes doivent rester prioritaires pour les cas critiques : valeurs manquantes, integrite, types, dates, outliers et transformations sensibles.

## Decision recommandee

Integrer maintenant le moteur hybride dans l'application. Garder le checkpoint LoRA comme artefact experimental, a reevaluer apres fusion ou service dedie. Ne pas attendre que le LLM seul soit parfait pour avancer sur le developpement produit.

## Fichiers produits

- Script de test : `ai_lab/final_capability_evaluation.py`
- Resultats detailles : `ai_lab/results/final_capability_evaluation/`
- Rapport technique : `ai_lab/results/final_capability_evaluation/RAPPORT_EVALUATION_FINALE.md`
