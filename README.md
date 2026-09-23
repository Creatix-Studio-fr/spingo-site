# SpinGO — version prête pour GitHub

Tous les fichiers sont au même niveau :

- app.py
- index.html
- style.css
- requirements.txt
- render.yaml
- README.md
- screenshot-1.png
- screenshot-2.png
- screenshot-3.png

## GitHub
Tu peux sélectionner tous les fichiers et les importer directement dans ton repository.

## Captures
Remplace les trois fichiers `screenshot-1.png`, `screenshot-2.png` et `screenshot-3.png` par tes captures.

## Render
Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn app:app`

Ajoute `DATABASE_URL` avec l'URL de ta base PostgreSQL Render.

Le site enregistre les inscriptions dans PostgreSQL lorsqu'il est déployé avec `DATABASE_URL`.


## Test rapide en local
Tu peux double-cliquer sur `index.html` : le design CSS et les captures fonctionneront directement.
Le formulaire, lui, nécessite le serveur Flask (`python app.py`) pour enregistrer les e-mails.

## Render
Le serveur Flask continue de servir `index.html` et `style.css`, donc les chemins relatifs fonctionnent aussi une fois le site en ligne.


## Correctif Render PostgreSQL
`app.py` force maintenant SQLAlchemy à utiliser `postgresql+psycopg://`.
Cela évite l'erreur `ModuleNotFoundError: No module named 'psycopg2'`.
