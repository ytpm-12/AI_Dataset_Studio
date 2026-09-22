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
