# AI Dataset Studio

Plateforme de préparation de jeux de données de qualité.

## Démarrage du backend sous Windows

Depuis la racine du projet :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

Le backend est disponible sur `http://127.0.0.1:8000/`.

Le contrat des routes testables avec Postman se trouve dans
[`docs/05_API/API_CONTRACT.md`](docs/05_API/API_CONTRACT.md).
La collection importable se trouve dans
[`docs/05_API/postman/AI_Dataset_Studio.postman_collection.json`](docs/05_API/postman/AI_Dataset_Studio.postman_collection.json).

## Architecture frontend

Le frontend cible est une application React + Vite, executee et geree avec Node.js.
Les templates Django actuels restent un prototype fonctionnel pendant sa construction
incrementale. Le frontend communiquera avec le backend via `/api/v1/`.

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

## Tests

```powershell
cd backend
python manage.py test
```
