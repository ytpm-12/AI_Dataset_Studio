# Collection Postman

Importer `AI_Dataset_Studio.postman_collection.json` dans Postman, puis executer les
requetes dans cet ordre :

1. `Auth / Obtenir le CSRF`
2. `Auth / Inscription` ou `Auth / Connexion`
3. `Projects / Creer un projet`
4. `Uploads / Importer un fichier`
5. `Jobs / Lister les traitements`
6. `Fin de parcours / Deconnexion`

La collection genere un utilisateur unique lors de l'inscription et conserve
automatiquement `csrfToken`, `projectId`, `uploadId` et `jobId`. Postman conserve
normalement les cookies `csrftoken` et `sessionid` pour `127.0.0.1`.

Avant un upload, selectionner manuellement un fichier CSV, JSON ou XML dans le champ
`file`. Le mot de passe de test peut etre modifie dans les variables de la collection.
