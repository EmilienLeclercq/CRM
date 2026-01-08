# CRM Lemonfive

CRM pipeline-first inspiré de Pipedrive.

## Architecture

- **Backend** : FastAPI + SQLAlchemy + Alembic + PostgreSQL (`apps/api`)
- **Frontend** : Next.js (`apps/web`)

## Démarrage rapide

### Backend (API)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

L’API démarre sur `http://localhost:8000`.

### Seed automatique

Au démarrage, si la base est vide :
- 1 workspace
- 1 admin (`admin@lemonfive.local` / `admin123`)
- 1 pipeline avec 5 stages
- 5 deals

### Frontend (Web)

```bash
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

L’interface est disponible sur `http://localhost:3000`.

## Endpoints principaux

- `POST /auth/login`
- `GET /auth/me`
- `GET /pipelines`
- `GET /stages?pipeline_id=...`
- `GET /deals`
- `PATCH /deals/{id}/stage`
