# Fine-tuning sur cloud GPU

Ces commandes sont à lancer dans un environnement Linux avec GPU, pas dans PowerShell local.

## 1. Upload

Uploader ce fichier dans l'environnement cloud :

```text
ai_lab/fine_tuning/ai_dataset_studio_finetune_pack.zip
```

## 2. Extraire

Commande portable, même si `unzip` n'est pas installé :

```bash
python -m zipfile -e ai_dataset_studio_finetune_pack.zip .
```

## 3. Installer

```bash
python -m pip install -U pip
pip install -U ms-swift transformers
```

## 4. Vérifier le GPU

```bash
python -c "import torch; print(torch.__version__); print('cuda=', torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no gpu')"
```

Continuer seulement si `cuda=True`.

## 5. Lancer le LoRA

```bash
DTYPE=float16 bash ai_lab/fine_tuning/run_ms_swift_sft.sh
```

## 6. A envoyer ensuite

Copier-coller les 30 dernières lignes du terminal, surtout le chemin du dernier
`checkpoint-...`.
