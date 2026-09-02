# Rapport de validation IA - Qwen3, LoRA et moteur hybride

Date : 2026-08-26

## Résumé exécutif

Les expérimentations montrent que Qwen3 peut être utilisé dans AI Dataset Studio, mais pas comme moteur autonome de décision. La solution la plus pertinente est un moteur hybride :

```text
profil statistique pandas
-> règles déterministes
-> Qwen3 / LoRA si le cas est ambigu ou non couvert
-> validation JSON
-> validation humaine avant transformation
```

Cette approche est plus fiable qu'un LLM seul, plus rapide sur les cas simples, et plus facile à expliquer à l'équipe.

## Objectif

L'objectif était de vérifier si un modèle local de type Qwen3 pouvait aider AI Dataset Studio à produire des recommandations de qualité de données :

- détection de valeurs manquantes;
- types mal interprétés;
- formats de dates ou nombres français;
- doublons;
- valeurs aberrantes;
- intégrité métier;
- préparation de variables pour machine learning;
- réponse JSON stricte conforme au schéma du projet.

## Ce qui a été réalisé

1. Installation et test de `qwen3:4b-instruct` via Ollama.
2. Création d'un benchmark spécialisé dans `ai_lab`.
3. Définition d'un schéma JSON de recommandation.
4. Création d'un prompt système métier pour AI Dataset Studio.
5. Création d'un moteur déterministe de recommandations.
6. Création d'un moteur hybride règles + LLM.
7. Génération d'un dataset supervisé pour fine-tuning.
8. Entraînement d'un adapter LoRA sur Kaggle GPU.
9. Sauvegarde du checkpoint LoRA `checkpoint-48`.
10. Tests sur datasets publics réels téléchargés depuis data.gouv.fr.

## Résultats synthétiques

### Qwen3 brut, zero-shot, 20 cas

Fichier de résultats : `ai_lab/results/zeroshot_limit20_v4_ctx2048.jsonl`

| Critère | Résultat |
|---|---:|
| Contrat JSON | 20/20, 100 % |
| Action correcte | 18/20, 90 % |
| Cible correcte | 20/20, 100 % |
| Paramètres corrects | 19/20, 95 % |
| Validation correcte | 19/20, 95 % |
| Exact global | 18/20, 90 % |
| Durée totale | 417,5 s |

Erreurs observées :

- `missing_numeric_symmetric` : le modèle a répondu `no_action` alors qu'une colonne avec `missing_ratio > 0` devait recevoir `impute_missing`.
- `numeric_outliers` : le modèle a proposé `scale_numeric` au lieu de `review_outliers`.

Conclusion : Qwen3 brut comprend bien le format, mais reste instable sur certaines décisions métier.

### Moteur hybride, 28 cas de test

Fichier de résultats : `ai_lab/results/user_hybrid_test_all_v1.jsonl`

| Critère | Résultat |
|---|---:|
| Contrat JSON | 28/28, 100 % |
| Action correcte | 28/28, 100 % |
| Cible correcte | 28/28, 100 % |
| Paramètres corrects | 28/28, 100 % |
| Validation correcte | 28/28, 100 % |
| Exact global | 28/28, 100 % |
| Durée | quasi instantanée sur les cas couverts par règles |

Conclusion : le moteur hybride est actuellement la meilleure base d'intégration produit.

## Fine-tuning LoRA

Le fine-tuning réalisé n'est pas du pré-entraînement. Il s'agit d'un SFT LoRA : Qwen3 reste le modèle de base, et un petit adapter apprend les exemples propres à AI Dataset Studio.

Artefact sauvegardé :

- `qwen3_ai_dataset_studio_lora_checkpoint_48.zip`
- checkpoint Kaggle : `checkpoint-48`
- fichiers essentiels vérifiés :
  - `adapter_config.json`
  - `adapter_model.safetensors`

Mini-test du checkpoint LoRA :

| Critère | Résultat |
|---|---:|
| Cas testés | 8 |
| Cas réussis | 7 |
| Score | 87,5 % |

Cas échoué :

- `missing_numeric_symmetric`
  - attendu : `impute_missing`
  - obtenu : `no_action`

Conclusion : le LoRA est prometteur, mais pas encore assez fiable pour remplacer les règles. Il doit être utilisé comme assistant complémentaire, ou ré-entraîné plus tard avec davantage de cas réels validés.

## Tests sur datasets publics réels

Commande reproduite par l'utilisateur :

```powershell
python ai_lab/profile_real_datasets.py "D:\Downloads\jeu de donnee\eco-counter-data.csv" "D:\Downloads\jeu de donnee\elecdom_courbes_horaires_detail_appareils.csv" --max-rows 50000 --output-jsonl ai_lab/results/real_world_recommendations_user_v1.jsonl
```

Fichier de résultats : `ai_lab/results/real_world_recommendations_user_v1.jsonl`

### Dataset 1 : eco-counter-data.csv

Profil :

- 50 000 lignes analysées;
- 9 colonnes;
- séparateur `;`;
- encodage `utf-8-sig`;
- données publiques de comptage, sans données personnelles directes.

Recommandations principales :

| Colonne | Problème détecté | Recommandation |
|---|---|---|
| `date` | format date/temps détecté | `standardize_format`, format `YYYY-MM-DD` |
| `isoDate` | format date/temps détecté | `standardize_format`, format `YYYY-MM-DD` |
| `counts` | 3,046 % de valeurs manquantes, distribution asymétrique, outliers | `impute_missing`, stratégie `median` |
| `status` | 3,046 % de valeurs manquantes | `impute_missing`, stratégie `mean` |
| `name` | 25,088 % de valeurs manquantes | `impute_missing`, stratégie `mode` |
| `sens` | 25,088 % de valeurs manquantes | `impute_missing`, stratégie `mean` |
| `counter` | 25,088 % de valeurs manquantes | `impute_missing`, stratégie `mode` |
| `geo` | 25,088 % de valeurs manquantes | `impute_missing`, stratégie `mode` |

Point de discussion : pour des colonnes comme `name`, `counter` et `geo`, l'imputation par mode est techniquement détectable, mais doit être validée métier. Dans une vraie application, il peut être préférable de proposer `request_human_review` ou une règle plus prudente pour les identifiants et coordonnées.

### Dataset 2 : elecdom_courbes_horaires_detail_appareils.csv

Profil :

- 624 lignes analysées;
- 7 colonnes;
- séparateur `;`;
- encodage `cp1252`;
- données agrégées de consommation électrique, sans données personnelles directes.

Recommandation principale :

| Colonne | Problème détecté | Recommandation |
|---|---|---|
| `consommation_Wh/h` | nombres stockés en texte avec virgule décimale française | `cast_type`, conversion vers `float` |

Conclusion : ce dataset valide un cas important pour un projet francophone : la conversion de nombres au format `39,4` vers un type numérique exploitable.

## Limites actuelles

- Les premiers tests réels sont qualitatifs : il n'existe pas encore de vérité terrain annotée pour ces datasets.
- Le profiler actuel supporte surtout CSV, XLS et XLSX. Le XML téléchargé n'est pas encore pris en charge.
- Le fichier `.xls` qualité de l'air nécessite l'installation de `xlrd`.
- Les règles déterministes doivent être affinées pour certaines colonnes métier : identifiants, coordonnées, codes, colonnes quasi constantes.
- Le checkpoint LoRA n'est pas encore intégré dans l'application web.

## Décision recommandée

Pour l'intégration dans AI Dataset Studio, la recommandation est :

1. intégrer d'abord le moteur hybride;
2. garder les règles déterministes comme source prioritaire;
3. utiliser Qwen3 ou Qwen3/LoRA pour les explications et les cas non couverts;
4. valider la sortie avec le schéma JSON;
5. garder une validation humaine avant toute transformation réelle de données.

Le fine-tuning LoRA doit être conservé comme artefact expérimental. Il pourra être amélioré après annotation de cas réels par l'équipe.

## Prochaine étape proposée

Intégrer le moteur hybride dans le projet applicatif avec trois fonctions principales :

1. `profile_dataset(file)` : lire un fichier tabulaire et produire les profils statistiques.
2. `recommend(profile)` : appliquer les règles déterministes, puis appeler le LLM si nécessaire.
3. `validate_recommendation(result)` : vérifier que la recommandation respecte le schéma JSON.

Cette étape permet de passer de l'expérimentation IA à une fonctionnalité produit démontrable.
