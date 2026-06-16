# DataInsight AI — Deployment Guide

## Frontend (Vercel)

1. Push repository to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Set root directory to `frontend`
4. Build settings:
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Environment variables:
   ```
   VITE_API_URL=https://your-backend.railway.app/api/v1
   ```
6. Deploy

## Backend (Railway)

1. Create new project on [Railway](https://railway.app)
2. Add PostgreSQL plugin
3. Deploy from `backend/` directory
4. Set environment variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/railway
DATABASE_URL_SYNC=postgresql://user:pass@host:5432/railway
SECRET_KEY=<generate-64-char-random-string>
CORS_ORIGINS=https://your-app.vercel.app
UPLOAD_DIR=/app/uploads
ENVIRONMENT=production
```

5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add persistent volume for `/app/uploads`

## Backend (Render)

1. Create Web Service from repo, root: `backend`
2. Runtime: Docker or Python
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database from Render dashboard
6. Configure same env vars as Railway

## Database (PostgreSQL)

Schema is auto-created on startup via SQLAlchemy `create_all`.

Tables:
- `users` — authentication & profiles
- `datasets` — uploaded files metadata & analysis cache
- `reports` — generated export files

## Docker Production

```bash
docker compose up --build -d
```

## Health Check

```
GET /api/health
```

## Post-Deploy Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Update `CORS_ORIGINS` with production frontend URL
- [ ] Configure persistent storage for uploads
- [ ] Set up SSL (handled by Vercel/Railway/Render)
- [ ] Create admin user or use seeded admin in dev only
- [ ] Run smoke test: register → upload → analyze → export

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Async PostgreSQL URL | `postgresql+asyncpg://...` |
| SECRET_KEY | JWT signing key | 64+ char random |
| CORS_ORIGINS | Allowed frontend origins | `https://app.vercel.app` |
| UPLOAD_DIR | File storage path | `/app/uploads` |
| MAX_UPLOAD_SIZE_MB | Upload limit | `50` |
| ENVIRONMENT | `development` or `production` | `production` |
