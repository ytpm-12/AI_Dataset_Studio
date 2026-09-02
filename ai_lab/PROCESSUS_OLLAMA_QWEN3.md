# Processus Ollama / Qwen3 pour AI Dataset Studio

Ce document décrit comment utiliser le modèle local Qwen3 avec Ollama pour AI Dataset
Studio. Les documents projet servent de contexte fonctionnel, mais les décisions IA
doivent rester validées par les tests et par l'utilisateur.

## Constat local

Modèle détecté :

- `qwen3:4b-instruct`
- 4.0B paramètres
- quantification `Q4_K_M`
- taille locale : environ 2.5 GB
- contexte annoncé par Ollama : 262144 tokens

Verdict court : ce modèle est suffisant pour le premier moteur IA du MVP si son rôle
reste limité à des recommandations structurées sur des profils statistiques produits par
pandas. Il ne doit pas devenir le moteur qui modifie directement les datasets.

## Ce que Qwen3 4B peut bien faire ici

- Proposer une action principale à partir d'un profil JSON déjà calculé.
- Expliquer brièvement une recommandation.
- Respecter un schéma JSON si la sortie est contrainte.
- Aider à prioriser des anomalies, valeurs manquantes, doublons ou formats incohérents.
- Tourner localement, ce qui réduit le risque d'exposer des données sensibles.

## Limites à respecter

- 4B reste petit pour des raisonnements métier ambigus ou multi-étapes.
- La quantification `Q4_K_M` favorise la légèreté, pas la précision maximale.
- Le modèle peut choisir `no_action` malgré une règle explicite si le prompt n'est pas
  assez démonstratif.
- Il ne faut pas lui envoyer le dataset complet quand un profil agrégé suffit.
- Il ne remplace pas pandas, les règles déterministes, les tests et la validation humaine.

## Protocole recommandé

1. Garder pandas comme moteur de vérité pour le profilage et les transformations.
2. Envoyer au modèle uniquement un profil JSON compact et anonymisé.
3. Contraindre la réponse avec `recommendation.schema.json`.
4. Utiliser `system_prompt.txt` comme source unique du prompt système.
5. Mesurer le modèle en zero-shot et few-shot.
6. Corriger le prompt et les règles déterministes avant d'envisager un fine-tuning.
7. Ajouter des cas réels anonymisés et revus humainement.
8. Séparer les exemples en entraînement, validation et test.
9. Fine-tuner seulement si les seuils restent insuffisants après amélioration du prompt.

## Commandes utiles 

Vérifier le modèle :

```powershell
ollama list
ollama show qwen3:4b-instruct
```

Vérifier si Ollama utilise le GPU pendant une génération :

```powershell
ollama ps
& "$env:windir\Sysnative\nvidia-smi.exe"
```

La colonne `PROCESSOR` de `ollama ps` doit indiquer `100% GPU` ou un mix
`CPU/GPU`. Si elle indique `100% CPU`, consulter les logs :

```powershell
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" -Tail 120
```

Si les logs contiennent `OLLAMA_LLM_LIBRARY:cpu_avx2`, Ollama est forcé en CPU.
Supprimer cette variable puis redémarrer Ollama :

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_LLM_LIBRARY", $null, "User")
[Environment]::SetEnvironmentVariable("OLLAMA_VULKAN", $null, "User")
Stop-Process -Name ollama -Force
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
```

Avec une carte 4 GB VRAM comme une GTX 1650, garder `--num-ctx 2048` pour les
tests du laboratoire. `--num-ctx 1024` peut être trop faible pour le prompt et le
schéma JSON.

Test rapide few-shot :

```powershell
python ai_lab/benchmark_ollama.py --limit 3
```

Comparaison zero-shot :

```powershell
python ai_lab/benchmark_ollama.py --limit 3 --no-few-shot --details
```

Sauvegarder les résultats détaillés :

```powershell
python ai_lab/benchmark_ollama.py --results-jsonl ai_lab/results/qwen3_4b_fewshot.jsonl
```

Tester un seul cas :

```powershell
python ai_lab/benchmark_ollama.py --case-id missing_categorical_mode --details
```

## Seuils de décision

- Si le few-shot atteint au moins 90 % exact, 95 % actions correctes et 95 % validations
  correctes sur des cas réels anonymisés : pas de fine-tuning.
- Si les actions sont au-dessus de 80 % mais les paramètres varient : améliorer le prompt,
  le schéma et les règles déterministes.
- Si les actions restent faibles après revue humaine des cas : préparer un fine-tuning.

## Préparer un vrai fine-tuning

Ollama sert le modèle, mais ne fine-tune pas directement. Un entraînement réaliste passe
plutôt par LoRA/QLoRA avec un outil spécialisé, puis export du modèle adapté vers GGUF
et création d'un modèle Ollama.

Format d'exemple recommandé :

```jsonl
{"messages":[{"role":"system","content":"...prompt système..."},{"role":"user","content":"Analyse ce profil et fournis une recommandation :\n{...profil JSON...}"},{"role":"assistant","content":"{\"action\":\"impute_missing\",\"target\":\"age\",\"parameters\":{\"strategy\":\"median\"},\"confidence\":0.92,\"explanation\":\"...\",\"requires_validation\":true}"}]}
```

Minimum pratique :

- 30 cas synthétiques servent seulement au laboratoire initial.
- 200 à 500 cas revus peuvent améliorer un comportement étroit.
- 1000+ cas variés donnent un signal nettement plus sérieux.
- Le jeu de test ne doit jamais être utilisé pour entraîner.

## Recommandation pour le MVP

Pour AI Dataset Studio, la meilleure trajectoire est :

1. Qwen3 4B local pour recommandations tabulaires structurées.
2. Règles pandas déterministes pour les cas évidents.
3. Validation humaine obligatoire avant toute transformation.
4. Benchmark continu avec export JSONL des résultats.
5. Fine-tuning seulement après collecte de cas réels anonymisés.
