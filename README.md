# AI Dataset Studio

Plateforme de préparation de jeux de données de qualité.

## Démarrage complet sous Windows

Docker Desktop doit etre ouvert. Depuis la racine du projet, une seule commande lance
Redis, Django, Celery et le frontend React :

```powershell
.\start-dev.ps1
```

L'application utilisateur est disponible sur `http://127.0.0.1:5173/`.
`http://127.0.0.1:8000/` est le backend et redirige vers React ; l'API reste sur
`http://127.0.0.1:8000/api/v1/` et l'administration sur `/admin/`.

### Démarrage manuel du backend

Depuis la racine du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

Le backend est disponible sur `http://127.0.0.1:8000/`, mais l'interface React doit
etre lancee dans un second terminal.

Le contrat des routes testables avec Postman se trouve dans
[`docs/05_API/API_CONTRACT.md`](docs/05_API/API_CONTRACT.md).
La collection importable se trouve dans
[`docs/05_API/postman/AI_Dataset_Studio.postman_collection.json`](docs/05_API/postman/AI_Dataset_Studio.postman_collection.json).

## Architecture frontend

Le frontend officiel est une application React + Vite, executee et geree avec Node.js.
Les anciens templates Django ont ete retires. React communique avec le backend via
`/api/v1/`.

### Demarrage du frontend

Dans un deuxieme terminal, depuis la racine du projet :

```powershell
cd frontend
npm install
npm run dev
```

Le frontend est disponible sur `http://127.0.0.1:5173/`. Vite transmet les requetes
`/api` et `/media` au backend Django local sur le port `8000`.

Verification du frontend :

```powershell
cd frontend
npm run lint
npm run build
```

## Worker Celery et Redis

Redis transporte les tâches entre Django et le worker Celery. Docker Desktop doit
être installé et démarré avant d'exécuter :

```powershell
docker compose up -d redis
docker compose ps
```

Dans un deuxième terminal, depuis `backend/` avec l'environnement virtuel activé :

```powershell
celery -A backend worker --loglevel=INFO --pool=solo
```

Le pool `solo` est utilisé pour garantir un comportement stable sous Windows.

Si Redis était indisponible pendant un upload, les fichiers restent en attente.
Après le redémarrage de Redis et du worker, les remettre dans la file avec :

```powershell
python manage.py enqueue_pending_uploads
```

Pour arrêter Redis sans supprimer ses données :

```powershell
docker compose down
```

## Parcours de demonstration MVP

1. Creer un compte puis un projet dans le frontend.
2. Importer un fichier CSV, JSON ou XML.
3. Attendre la validation et consulter l'apercu et le profil.
4. Analyser puis supprimer les doublons dans une nouvelle version.
5. Traiter les valeurs manquantes par colonne.
6. Convertir un type de colonne si necessaire.
7. Calculer le rapport qualite.
8. Exporter le resultat en CSV ou JSON.
9. Verifier l'historique et revenir au fichier source a tout moment.

Chaque transformation exige une confirmation et cree un nouveau dataset : le fichier
source n'est jamais ecrase.

## Assistant IA hybride

Par defaut, le backend utilise Ollama et le modele local `qwen3:4b-instruct` :

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434
AI_MODEL_NAME=qwen3:4b-instruct
AI_REQUEST_TIMEOUT_SECONDS=120
```

Le moteur applique d'abord les regles deterministes. Qwen intervient pour les cas
non couverts ou sur demande explicite. Les reponses sont validees par un contrat JSON,
journalisees et ne declenchent jamais une transformation automatique.

L'adapter LoRA `ai_lab/qwen3_ai_dataset_studio_lora_checkpoint_48.zip` doit etre servi
par ms-swift/vLLM avec un endpoint compatible OpenAI. Pour basculer vers ce service :

```env
AI_PROVIDER=openai_compatible
AI_BASE_URL=http://127.0.0.1:8000
AI_MODEL_NAME=qwen3-ai-dataset-studio
AI_API_KEY=
```

Le code applicatif et l'interface restent identiques : seules ces variables changent.

## Tests

```powershell
cd backend
python manage.py test
```
