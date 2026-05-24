#  InfraPilot — Cloud Deployment & Monitoring Platform

[![CI Pipeline](https://github.com/yourusername/infrapilot/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/infrapilot/actions)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://docker.com)

> **InfraPilot** is a full-stack DevOps platform that monitors backend services, tracks deployments, and centralizes operational visibility — built to simulate a real internal engineering tool used by cloud/DevOps teams.

---

## 📸 Screenshots

> _Add your screenshots here after running the project locally_
>
> - `docs/screenshots/dashboard.png` — Main monitoring dashboard
> - `docs/screenshots/services.png` — Service health table
> - `docs/screenshots/deployments.png` — Deployment history
> - `docs/screenshots/incidents.png` — Incident management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│                    React + Vite (SPA)                           │
│              Deployed on: Vercel (free tier)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST (JSON)
                           │ VITE_API_URL
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│              Python 3.12 + SQLAlchemy (async)                  │
│               Deployed on: Render (free tier)                  │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│   │   Routers    │  │   Services   │  │   Background     │    │
│   │  /services   │  │  monitoring  │  │  Health Checker  │    │
│   │ /deployments │  │  health_chk  │  │  (asyncio loop)  │    │
│   │  /incidents  │  └──────────────┘  └──────────────────┘    │
│   │ /environments│                                              │
│   └──────────────┘                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQLAlchemy ORM (async)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  SQLite (local dev / Render free)                               │
│  OR PostgreSQL (Docker Compose / production upgrade)            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts Demonstrated

| Concept | Implementation |
|---|---|
| **REST API design** | FastAPI routers, HTTP verbs, status codes |
| **Async Python** | `asyncio`, `async/await`, `aiohttp` for concurrent health checks |
| **ORM** | SQLAlchemy 2.0 with async sessions |
| **Pydantic validation** | Request/response schemas separate from DB models |
| **Background tasks** | `asyncio.create_task()` — health checker loop |
| **Dependency injection** | FastAPI `Depends(get_db)` pattern |
| **Containerization** | Multi-stage Dockerfiles, Docker Compose networking |
| **CI/CD** | GitHub Actions: lint → test → build → deploy |
| **Environment management** | `.env` files, Pydantic BaseSettings, 12-factor app |
| **Middleware** | Request logging, CORS |
| **SPA routing** | React Router + nginx `try_files` |

---

## 🚀 Quick Start (Local Development)

### Option A: Run with Docker Compose (Recommended)

The fastest way — one command starts everything.

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/infrapilot.git
cd infrapilot

# 2. Copy env files
cp .env.example .env

# 3. Start everything
docker compose up --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

To stop: `docker compose down`
To reset data: `docker compose down -v` (removes volumes)

---

### Option B: Run Manually (VS Code / Local Python + Node)

Best for active development — you get hot-reload on both frontend and backend.

#### Prerequisites

- Python 3.12+ — [python.org](https://python.org)
- Node.js 20+ — [nodejs.org](https://nodejs.org)
- Git

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create a virtual environment
# (Keeps project dependencies isolated from your system Python)
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     InfraPilot backend starting up...
INFO:     Database tables ready
INFO:     Background health checker started
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Visit **http://localhost:8000/docs** for the interactive API documentation.

#### Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install Node packages
npm install

# Copy env config
cp .env.example .env.local

# Start the dev server (hot-reload enabled)
npm run dev
```

Visit **http://localhost:5173**

---

## 📁 Project Structure

```
infrapilot/
│
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                   # App entry point, startup, routers
│   │   ├── config.py                 # Settings from environment variables
│   │   ├── database.py               # DB engine, session, Base model
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models (DB tables)
│   │   │   ├── service.py
│   │   │   ├── deployment.py
│   │   │   ├── incident.py
│   │   │   └── environment.py
│   │   │
│   │   ├── schemas/                  # Pydantic schemas (API request/response)
│   │   │   ├── service.py
│   │   │   ├── deployment.py
│   │   │   ├── incident.py
│   │   │   └── environment.py
│   │   │
│   │   ├── routers/                  # API route handlers
│   │   │   ├── health.py             # /health, /health/live, /health/ready
│   │   │   ├── services.py           # /api/v1/services
│   │   │   ├── deployments.py        # /api/v1/deployments
│   │   │   ├── incidents.py          # /api/v1/incidents
│   │   │   └── environments.py       # /api/v1/environments
│   │   │
│   │   ├── services/                 # Business logic
│   │   │   ├── health_checker.py     # Background monitoring loop
│   │   │   └── monitoring.py         # Dashboard stats
│   │   │
│   │   ├── middleware/
│   │   │   └── logging_middleware.py # Request logging
│   │   │
│   │   └── utils/
│   │       └── logger.py             # Logging configuration
│   │
│   ├── tests/
│   │   └── test_api.py               # pytest integration tests
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   └── .env.example
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── main.jsx                  # App entry point
│   │   ├── App.jsx                   # Router setup
│   │   ├── index.css                 # Global styles + design tokens
│   │   │
│   │   ├── api/
│   │   │   └── client.js             # Axios API client
│   │   │
│   │   ├── hooks/
│   │   │   └── useApi.js             # Custom hooks (useApi, useAutoRefresh)
│   │   │
│   │   ├── components/
│   │   │   └── common/               # Reusable components
│   │   │       ├── Layout.jsx        # Sidebar + top bar
│   │   │       ├── StatCard.jsx      # Dashboard metric card
│   │   │       ├── Toast.jsx         # Notifications
│   │   │       └── States.jsx        # Loading/Error/Empty states
│   │   │
│   │   ├── pages/                    # Page components (one per route)
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ServicesPage.jsx
│   │   │   ├── DeploymentsPage.jsx
│   │   │   ├── IncidentsPage.jsx
│   │   │   └── EnvironmentsPage.jsx
│   │   │
│   │   └── utils/
│   │       └── format.js             # Date/number formatters
│   │
│   ├── index.html
│   ├── vite.config.js
│   ├── nginx.conf                    # nginx SPA routing config
│   ├── Dockerfile
│   ├── vercel.json                   # Vercel deployment config
│   └── .env.example
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI: lint + test + Docker build
│       └── deploy.yml                # CD: deploy to Render + Vercel
│
├── docker-compose.yml                # Full stack local setup
├── render.yaml                       # Render.com IaC config
├── .env.example                      # Root env vars for Docker Compose
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./infrapilot.db` | DB connection string |
| `SECRET_KEY` | _(required)_ | JWT/security secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENVIRONMENT` | `development` | `development` \| `staging` \| `production` |
| `DEBUG` | `true` | Enables SQL query logging |
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | CORS whitelist — add your frontend URL |
| `HEALTH_CHECK_INTERVAL` | `60` | Seconds between health check cycles |
| `HEALTH_CHECK_TIMEOUT` | `10` | Per-request timeout in seconds |
| `LOG_LEVEL` | `INFO` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## 🐳 Docker Guide

### Build and run manually

```bash
# Build backend image
docker build -t infrapilot-backend ./backend

# Build frontend image
docker build -t infrapilot-frontend ./frontend \
  --build-arg VITE_API_URL=http://localhost:8000

# Run backend
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite+aiosqlite:////data/infrapilot.db \
  -v $(pwd)/data:/data \
  infrapilot-backend

# Run frontend
docker run -p 3000:80 infrapilot-frontend
```

### Docker Compose commands

```bash
# Start all services (rebuild images if code changed)
docker compose up --build

# Start in background (detached mode)
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop all services
docker compose down

# Stop and delete all data (volumes)
docker compose down -v

# Restart just the backend
docker compose restart backend

# Execute a command inside a running container
docker compose exec backend python -c "from app.database import create_tables; import asyncio; asyncio.run(create_tables())"
```

---

## 🔄 GitHub Actions CI/CD

### CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:

```
Push/PR → backend-ci ──────┐
              │             ├──→ docker-build (smoke test)
          frontend-ci ──────┘
```

**Steps:**
1. **backend-ci**: Runs `ruff` linter + `pytest` tests
2. **frontend-ci**: Runs `eslint` + `vite build`
3. **docker-build**: Builds both Docker images, runs health check

### Deploy Pipeline (`.github/workflows/deploy.yml`)

Runs only when merging to `main`:

1. Triggers Render deployment via API
2. Deploys frontend to Vercel via CLI
3. Posts summary to GitHub

### Required GitHub Secrets

Add these in: **GitHub repo → Settings → Secrets and variables → Actions**

| Secret | How to get it |
|---|---|
| `RENDER_API_KEY` | render.com → Account Settings → API Keys |
| `RENDER_SERVICE_ID` | render.com → Your service → URL contains `srv-xxxxx` |
| `VERCEL_TOKEN` | vercel.com → Settings → Tokens |
| `VERCEL_ORG_ID` | vercel.com → Settings → General → Team ID |
| `VERCEL_PROJECT_ID` | vercel.com → Your project → Settings → General |

---

## ☁️ Deployment

### Deploy Backend to Render (Free)

1. Create account at [render.com](https://render.com)
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (copy from `backend/.env.example`)
6. Click **Create Web Service**

> ⚠️ Free tier **spins down** after 15 minutes of inactivity. First request after sleep takes ~30s. For always-on, upgrade to the paid tier ($7/mo).

### Deploy Frontend to Vercel (Free)

1. Create account at [vercel.com](https://vercel.com)
2. Click **Add New → Project**
3. Import your GitHub repo
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - `VITE_API_URL` = `https://your-render-service.onrender.com`
6. Click **Deploy**

> After deploying, update `ALLOWED_ORIGINS` in your Render backend to include your Vercel URL.

---

## 📡 API Reference

Base URL: `http://localhost:8000` (local) or your Render URL

> Interactive docs available at `/docs` (Swagger UI) and `/redoc`

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Full health check (app + DB) |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe |

### Services

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/services/` | List all services |
| `POST` | `/api/v1/services/` | Register new service |
| `GET` | `/api/v1/services/{id}` | Get service details |
| `PATCH` | `/api/v1/services/{id}` | Update service |
| `DELETE` | `/api/v1/services/{id}` | Remove service |
| `POST` | `/api/v1/services/{id}/check` | Trigger manual health check |
| `GET` | `/api/v1/services/stats/summary` | Dashboard stats |

### Deployments

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/deployments/` | List deployments |
| `POST` | `/api/v1/deployments/` | Record deployment |
| `GET` | `/api/v1/deployments/{id}` | Get deployment |
| `PATCH` | `/api/v1/deployments/{id}` | Update status |

### Incidents

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/incidents/` | List incidents |
| `POST` | `/api/v1/incidents/` | Create incident |
| `PATCH` | `/api/v1/incidents/{id}` | Update/resolve incident |

### Environments

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/environments/` | List environments |
| `POST` | `/api/v1/environments/` | Create environment |
| `DELETE` | `/api/v1/environments/{id}` | Delete environment |

### Example API Calls

```bash
# Register a service to monitor
curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My API", "url": "https://httpbin.org/status/200", "environment": "production"}'

# Trigger a manual health check
curl -X POST http://localhost:8000/api/v1/services/{id}/check

# Record a deployment
curl -X POST http://localhost:8000/api/v1/deployments/ \
  -H "Content-Type: application/json" \
  -d '{"service_id": "...", "service_name": "My API", "version": "v2.0.0", "environment": "production", "branch": "main"}'
```

---

## 🧪 Running Tests

```bash
cd backend

# Activate virtual environment first
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test
pytest tests/test_api.py::test_create_service -v
```

---

## 🔧 VS Code Setup

### Recommended Extensions

Install these for the best development experience:

- **Python** (Microsoft) — IntelliSense, debugging
- **Pylance** — Type checking
- **Ruff** — Fast Python linting
- **ESLint** — JavaScript linting
- **Prettier** — Code formatting
- **Docker** (Microsoft) — Docker file syntax, container management
- **REST Client** — Test API endpoints from VS Code
- **GitLens** — Enhanced Git history

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["backend/tests"]
}
```

### Debugging the Backend

Create `.vscode/launch.json`:

```json
{
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "env": { "PYTHONPATH": "${workspaceFolder}/backend" }
    }
  ]
}
```

---

## 🔮 Future Improvements

Here are ideas for extending this project (great for continued learning):

| Feature | Complexity | Tech to learn |
|---|---|---|
| **User authentication** | Medium | JWT, bcrypt, OAuth2 |
| **Real-time updates** | Medium | WebSockets, SSE |
| **Email/Slack alerts** | Easy | SMTP, Slack API |
| **Metrics charts** | Easy | Recharts time series |
| **PostgreSQL migration** | Easy | asyncpg, Alembic |
| **Alembic migrations** | Medium | Database versioning |
| **API key auth** | Medium | FastAPI security |
| **Multi-user teams** | Hard | RBAC, multi-tenancy |
| **Terraform IaC** | Hard | Infrastructure as Code |
| **Prometheus metrics** | Medium | `/metrics` endpoint |
| **Grafana dashboard** | Medium | Observability stack |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

The CI pipeline will run automatically on your PR.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙋 Getting Help

- **API not responding?** Check `docker compose logs backend`
- **Frontend blank page?** Open browser DevTools → Console for errors
- **CORS errors?** Make sure `ALLOWED_ORIGINS` in backend includes your frontend URL
- **Database errors?** Delete `infrapilot.db` and restart (dev only)
- **Port already in use?** Change ports in `docker-compose.yml`

---

Built with ❤️ as a portfolio/learning project. Designed to demonstrate real-world DevOps and full-stack engineering patterns.
