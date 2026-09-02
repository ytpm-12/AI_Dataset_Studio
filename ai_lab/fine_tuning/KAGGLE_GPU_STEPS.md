# Fine-tuning sur Kaggle sans Google Drive

Ce chemin contourne l'erreur Colab `Drive storage quota`.

## 1. Creer le dataset prive

1. Aller sur Kaggle.
2. Ouvrir `Datasets`.
3. Cliquer `New Dataset`.
4. Uploader `ai_lab/fine_tuning/ai_dataset_studio_finetune_pack.zip`.
5. Garder le dataset en `Private`.
6. Cliquer `Create`.

## 2. Creer le notebook

1. Ouvrir `Code`.
2. Cliquer `New Notebook`.
3. Dans `Settings`, mettre `Accelerator` sur `GPU`.
4. Dans le panneau `Input`, cliquer `Add Input`.
5. Ajouter le dataset prive cree a l'etape 1.

## 3. Lancer les cellules

Importer ou recopier les cellules de :

```text
ai_lab/fine_tuning/AI_Dataset_Studio_FineTune_Kaggle.ipynb
```

Commencer par la cellule `Verifier que le GPU est actif`.

## 4. Ce que tu dois m'envoyer

Envoie-moi la sortie de la cellule GPU.

Continuer seulement si elle affiche :

```text
cuda= True
```

## Correction P100

Si Kaggle affiche `Tesla P100-PCIE-16GB` avec un avertissement `sm_60 is not compatible`,
installer PyTorch CUDA 11.8 avant `ms-swift` :

```bash
pip uninstall -y torch torchvision torchaudio
pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
```

Ne pas redemarrer la session Kaggle apres cette installation : Kaggle peut restaurer son
image Python de base. Verifier avec un sous-processus :

```bash
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Si cette commande affiche `2.5.1+cu118`, continuer dans la meme session.

## Correction ms-swift 4.x

Si l'erreur affiche :

```text
ValueError: remaining_argv: ['--train_type', 'lora']
```

Corriger le script dans `/kaggle/working` :

```bash
sed -i 's/--train_type/--tuner_type/g' ai_lab/fine_tuning/run_ms_swift_sft.sh
```

## Correction torchao Kaggle

Si l'erreur affiche :

```text
ImportError: Found an incompatible version of torchao
```

Retirer le paquet Kaggle incompatible :

```bash
pip uninstall -y torchao
```

Puis relancer le mini-test dans la meme session.

## Correction FSDPModule avec P100

Si l'erreur affiche :

```text
ImportError: cannot import name 'FSDPModule' from 'torch.distributed.fsdp'
```

Installer PyTorch 2.6.0 CUDA 11.8, compatible avec l'API attendue par `ms-swift 4.x` :

```bash
pip uninstall -y torch torchvision torchaudio torchao
pip install --no-cache-dir --force-reinstall torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no gpu'); from torch.distributed.fsdp import FSDPModule; print('FSDPModule OK')"
```

Ne pas redemarrer Kaggle apres cette correction.

Si `pip` affiche des conflits `fsspec`, `numpy` ou `pillow`, les corriger sans changer Torch :

```bash
pip install --no-cache-dir "fsspec<=2026.2.0,>=2023.1.0" "numpy<2.4,>=1.22" "pillow<12.0,>=8.0"
python -c "import torch; from torch.distributed.fsdp import FSDPModule; print(torch.__version__, torch.cuda.is_available(), 'FSDPModule OK')"
```

## Si `/kaggle/working/ai_lab` disparait

Kaggle a probablement redemarre la session. Refaire dans l'ordre :

```bash
pip uninstall -y torch torchvision torchaudio torchao
pip install --no-cache-dir --force-reinstall torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
```

Puis recopier le dataset :

```python
from pathlib import Path
import shutil

src = Path("/kaggle/input/datasets/princemigwel/ai-data-studio")
dst = Path("/kaggle/working")
shutil.copytree(src / "ai_lab", dst / "ai_lab", dirs_exist_ok=True)
```

Puis corriger le script :

```bash
sed -i 's/--train_type/--tuner_type/g' /kaggle/working/ai_lab/fine_tuning/run_ms_swift_sft.sh
```
