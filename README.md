# DataInsight AI

Production-ready, AI-powered data analysis platform. Upload datasets, get automatic insights, create visualizations, run ML predictions, chat with an AI assistant, and export professional reports.

## Features

- **Authentication** — JWT register/login, protected routes, user profiles
- **Dataset Upload** — CSV, Excel (.xlsx), JSON with validation
- **Automatic Analysis** — Stats, correlations, missing values, duplicates, quality score
- **Visualizations** — Bar, line, pie, scatter, histogram, heatmap (Plotly)
- **AI Assistant** — Natural language Q&A about your data
- **ML Predictions** — Regression & classification with metrics
- **Data Cleaning** — Preview & apply transformations
- **Export Reports** — PDF, Excel, Word, CSV
- **Admin Panel** — User/dataset monitoring
- **Responsive UI** — Dark/light mode, mobile-friendly SaaS design

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React, Vite, TypeScript, Tailwind CSS, Plotly.js, Axios |
| Backend | Python, FastAPI, Pandas, NumPy, Scikit-learn |
| Database | PostgreSQL |
| Auth | JWT + bcrypt |

## Project Structure

```
data_science/
├── frontend/          # React SPA
├── backend/           # FastAPI API
├── sample_data/       # Sample CSV for testing
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL (or Docker)

### 1. Start Database (Docker)

```bash
docker compose up db -d
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/api/docs

**Default admin (dev):** `admin@datainsight.ai` / `Admin123!`

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: http://localhost:5173

### 4. Full Stack with Docker

```bash
docker compose up --build
```

## Sample Data

Upload `sample_data/sales_data.csv` to test analysis, charts, AI chat, and predictions (use `sales` or `revenue` as target columns).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Profile |
| POST | `/api/v1/datasets/upload` | Upload dataset |
| GET | `/api/v1/datasets/{id}/analysis` | Auto analysis |
| POST | `/api/v1/charts/{id}` | Generate chart |
| POST | `/api/v1/chat/{id}` | AI assistant |
| POST | `/api/v1/predictions/{id}` | ML prediction |
| POST | `/api/v1/cleaning/{id}/preview` | Preview cleaning |
| POST | `/api/v1/reports/{id}/export` | Export report |
| GET | `/api/v1/dashboard` | Dashboard stats |
| GET | `/api/v1/admin/stats` | Admin stats |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Vercel (frontend), Railway/Render (backend), and PostgreSQL setup.

## Security

- JWT authentication with refresh tokens
- bcrypt password hashing
- File type & size validation
- Rate limiting (SlowAPI)
- CORS protection
- SQL injection protection via SQLAlchemy ORM
- Input sanitization via Pydantic

## License

MIT
