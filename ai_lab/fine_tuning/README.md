# Fine-tuning Qwen3 pour AI Dataset Studio

Objectif : adapter Qwen3 à la sortie JSON stricte de AI Dataset Studio.

## En clair

Ce n'est pas du pré-entraînement. Le pré-entraînement apprend une langue et le monde
à partir de masses énormes de texte : ce n'est pas réaliste pour nous.

Ce que nous faisons ici est un fine-tuning SFT avec LoRA : on garde Qwen3 comme base,
et on entraîne un petit adapter spécialisé sur nos exemples :

- lire un profil statistique tabulaire;
- choisir une action autorisée;
- remplir `target`, `parameters` et `requires_validation` correctement;
- répondre en JSON strict.

Le gain attendu n'est pas de rendre le CPU plus rapide. Le gain attendu est surtout :

- moins d'erreurs de décision en mode LLM pur;
- moins besoin de few-shot long;
- comportement plus stable sur les cas récurrents du projet.

## Point important

Ollama sert le modèle en local, mais ne réalise pas le fine-tuning. Le fine-tuning se fait
avec un outil d'entraînement comme `ms-swift`, puis le résultat peut être exporté et
réutilisé ensuite.

La machine locale actuelle n'est pas idéale pour l'entraînement :

- Ollama tourne encore en CPU.
- La GTX 1650 a 4 GB de VRAM, trop juste pour entraîner confortablement Qwen3 4B.
- Pour gagner du temps, utiliser un environnement cloud Linux avec GPU NVIDIA.

## Fichiers prêts

- `ai_lab/training/qwen3_sft_train.jsonl`
- `ai_lab/training/qwen3_sft_validation.jsonl`
- `ai_lab/training/qwen3_sft_test.jsonl`

Ces fichiers utilisent le format `messages`, compatible avec les formats SFT courants.

## Environnement recommandé

Minimum pratique :

- Linux
- Python 3.11+
- GPU NVIDIA avec 16 GB VRAM ou plus
- 24 GB VRAM conseillé pour travailler plus confortablement

## Installation

```bash
python -m pip install -U pip
pip install -U ms-swift transformers
```

## Entraînement LoRA

Depuis la racine du projet :

```bash
bash ai_lab/fine_tuning/run_ms_swift_sft.sh
```

Sur Windows PowerShell, si `swift: command not found` apparaît :

```powershell
.\ai_lab\fine_tuning\run_ms_swift_sft.ps1
```

Si PowerShell bloque le script local :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\ai_lab\fine_tuning\run_ms_swift_sft.ps1
```

Le script utilise par défaut :

- modèle : `Qwen/Qwen3-4B-Instruct-2507`
- méthode : LoRA
- train : `ai_lab/training/qwen3_sft_train.jsonl`
- validation : `ai_lab/training/qwen3_sft_validation.jsonl`
- sortie : `ai_lab/fine_tuning/output/qwen3_ai_dataset_studio_lora`

## Servir le checkpoint entraîné

Après entraînement, repérer le dernier dossier `checkpoint-...`, puis lancer :

```bash
ADAPTER=ai_lab/fine_tuning/output/qwen3_ai_dataset_studio_lora/vx-xxx/checkpoint-xxx \
bash ai_lab/fine_tuning/serve_ms_swift_adapter.sh
```

Le serveur expose par défaut une API OpenAI-compatible sur :

```text
http://127.0.0.1:8000/v1/chat/completions
```

## Après entraînement

Tester le dernier checkpoint avec le même benchmark :

```powershell
python ai_lab/benchmark_ollama.py --api openai --url http://127.0.0.1:8000/v1/chat/completions --model qwen3-ai-dataset-studio --engine llm --cases ai_lab/training/cases_test.jsonl --no-few-shot --details --results-jsonl ai_lab/results/finetuned_test_v1.jsonl
```

Le modèle fine-tuné doit surtout corriger les erreurs observées avec Qwen3 pur :

- validation humaine oubliée pour `cast_type`;
- cible équilibrée confondue avec déséquilibre;
- petit échantillon traité comme outlier certain;
- faible taux de valeurs manquantes traité comme `no_action`.

## Critère de décision

Le fine-tuning est utile seulement s'il dépasse clairement Qwen3 zero-shot :

- exact >= 90 %
- action >= 95 %
- validation >= 95 %
- pas d'erreur serveur

Même avec fine-tuning, le moteur recommandé pour le produit reste hybride :

1. règles déterministes;
2. Qwen3 pour explication ou cas ambigu;
3. validation humaine avant transformation.
