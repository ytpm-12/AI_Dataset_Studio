# Laboratoire IA

Ce dossier sert à évaluer le modèle local avant tout entraînement. Il ne contient ni modèle, ni environnement virtuel, ni donnée privée.

## Contenu

- `recommendation.schema.json` définit le contrat de sortie strict de l'assistant.
- `evaluation_cases.jsonl` contient 30 profils synthétiques et leurs réponses attendues.
- `benchmark_ollama.py` interroge Ollama et mesure les écarts sans dépendance Python externe.
- `prepare_supervised_dataset.py` génère un JSONL supervisé utilisable comme base de fine-tuning.
- `PROCESSUS_OLLAMA_QWEN3.md` décrit la démarche recommandée pour Qwen3, Ollama et un éventuel fine-tuning.

## Lancer un test rapide

Ollama doit être démarré et le modèle `qwen3:4b-instruct` doit être installé.

```powershell
python ai_lab/benchmark_ollama.py --limit 3
```

Le mode par défaut ajoute quatre exemples supervisés distincts des cas d'évaluation. Ils montrent au modèle la forme et la logique des réponses attendues sans modifier ses poids.

Pour exécuter les 30 cas :

```powershell
python ai_lab/benchmark_ollama.py
```

Pour mesurer le modèle sans exemples et comparer les résultats :

```powershell
python ai_lab/benchmark_ollama.py --no-few-shot
```

Ajoutez `--details` pour afficher la réponse JSON complète de chaque cas en écart.
Utilisez `--case-id missing_categorical_mode` pour rejouer un seul cas. Une erreur serveur Ollama est relancée une fois par défaut.

Le benchmark utilise `system_prompt.txt` comme prompt système, une température nulle, désactive le raisonnement long et demande à l'API Ollama une sortie conforme au schéma JSON.

Pour conserver les réponses détaillées :

```powershell
python ai_lab/benchmark_ollama.py --results-jsonl ai_lab/results/qwen3_4b_fewshot.jsonl
```

## Mode accéléré

Le mode `rules` évalue les règles déterministes sans appeler Ollama :

```powershell
python ai_lab/benchmark_ollama.py --engine rules --limit 30 --details --results-jsonl ai_lab/results/rules_limit30.jsonl
```

Le mode `hybrid` applique d'abord les règles déterministes. Qwen3 sert ensuite de secours pour les profils non couverts :

```powershell
python ai_lab/benchmark_ollama.py --engine hybrid --limit 30 --no-few-shot --num-ctx 2048 --details --results-jsonl ai_lab/results/hybrid_limit30.jsonl
```

Pour préparer le JSONL supervisé :

```powershell
python ai_lab/prepare_supervised_dataset.py --output ai_lab/training/qwen3_recommendations_sft.jsonl
```

Pour générer rapidement un corpus augmenté et ses splits :

```powershell
python ai_lab/augment_training_cases.py --variants-per-case 5 --output-dir ai_lab/training
```

Cette commande produit :

- `ai_lab/training/cases_augmented.jsonl`
- `ai_lab/training/cases_train.jsonl`
- `ai_lab/training/cases_validation.jsonl`
- `ai_lab/training/cases_test.jsonl`

Puis générez les fichiers conversationnels SFT :

```powershell
python ai_lab/prepare_supervised_dataset.py --cases ai_lab/training/cases_train.jsonl --output ai_lab/training/qwen3_sft_train.jsonl
python ai_lab/prepare_supervised_dataset.py --cases ai_lab/training/cases_validation.jsonl --output ai_lab/training/qwen3_sft_validation.jsonl
python ai_lab/prepare_supervised_dataset.py --cases ai_lab/training/cases_test.jsonl --output ai_lab/training/qwen3_sft_test.jsonl
```

## Seuil de décision initial

- Au moins 90 % de réponses entièrement exactes, 95 % d'actions correctes et 95 % de validations correctes : pas de fine-tuning.
- Au moins 80 % d'actions et 90 % de validations correctes : améliorer d'abord le prompt et les règles déterministes.
- En dessous : le fine-tuning devient un candidat, après création et revue humaine d'un jeu de données réel séparé en entraînement, validation et test.

Ces seuils donnent un premier signal. Les 30 cas synthétiques ne remplacent pas une évaluation sur des cas réels anonymisés.

## Démarche

1. Mesurer les réponses du modèle actuel.
2. Examiner et corriger les réponses attendues avec un expert humain.
3. Enrichir les cas avec des situations réelles anonymisées.
4. Séparer ensuite les exemples en jeux d'entraînement, validation et test.
5. Ne préparer un fine-tuning que si le prompt et le RAG ne suffisent pas.
