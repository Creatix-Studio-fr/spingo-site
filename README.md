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
