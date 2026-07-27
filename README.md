# NuruCare

## AI-Powered Contraceptive Decision-Support Platform for Sub-Saharan Africa

> *"Nuru" means "Light" in Swahili illuminating informed contraceptive choices.*

## Overview

NuruCare is an ethical, explainable AI platform that helps individuals in Sub-Saharan Africa make safer, personalized and informed contraceptive choices based on their health profiles, preferences and reproductive goals. The project prioritizes privacy, safety and accessibility.

## Features

- ✅ **Intelligent Intake Form** - Structured 8-step health questionnaire
- ✅ **WHO MEC Safety Rules** - Clinical guardrails (WHO Medical Eligibility Criteria 2024)
- ✅ **RAG + Gemini Flash** - Personalized, context-aware recommendations
- ✅ **Multilingual** - English + Swahili support
- ✅ **Offline Capable** - PWA with service workers
- ✅ **Privacy First** - Cryptographic sync tokens, 15-min nurse keys, anonymous profiles
- ✅ **Partner Sync** - Token-based anonymous partner profile linking
- ✅ **Nurse Handoff** - Secure temporary nurse access with time-limited session keys

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19 + Tailwind CSS + Vite + PWA |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL (with pgvector) + Supabase (optional hosted option) |
| AI | Google Gemini Flash API |
| Deployment | Docker + Docker Compose + Nginx |
| CI/CD | GitHub Actions |

## Project Structure

```
nurucare/
├── backend/                # FastAPI backend application
│   ├── api/
│   │   ├── endpoints/      # API route definitions (intake, sync, etc.)
│   │   │   ├── __init__.py
│   │   │   ├── intake.py   # Intake-related endpoints
│   │   │   └── sync.py     # Partner sync token endpoints (separate from main.py)
│   │   ├── schemas/        # Pydantic models for API payloads
│   │   │   ├── __init__.py
│   │   │   └── profile.py  # Profile data schemas
│   │   └── __init__.py
│   ├── db/                 # Database utilities
│   │   ├── __init__.py
│   │   ├── database.py     # Alternative database module (duplicate of ../database.py)
│   │   ├── schema.sql      # Database schema definitions
│   │   └── test_vector_db.py # Vector DB tests
│   ├── engine/             # AI/recommendation logic
│   │   ├── __init__.py
│   │   ├── guardrail.py    # WHO MEC safety rules implementation
│   │   ├── guardrail_backup.py # Backup guardrail logic
│   │   ├── rag_pipeline.py # RAG (Retrieval-Augmented Generation) pipeline
│   │   ├── recommendation_pipeline.py # Full recommendation workflow
│   │   └── who_mec_rules.json # WHO MEC rule definitions
│   ├── prompts/            # AI prompt templates
│   │   └── optimized_prompts.py # Optimized prompts for Gemini
│   ├── scripts/            # Utility scripts
│   │   ├── __init__.py
│   │   └── create_embeddings.py # Create embeddings for knowledge base
│   ├── sync/               # Partner sync logic
│   │   └── partner_sync.py # Cryptographic sync token generation/validation
│   ├── tests/              # Backend unit tests
│   │   ├── __init__.py
│   │   └── test_guardrail_simple.py # Guardrail logic tests
│   ├── __init__.py
│   ├── ai_client.py        # Gemini API client integration
│   ├── app.py              # Secondary FastAPI app (duplicate of main.py in some areas)
│   ├── auth.py             # Authentication (JWT, nurse accounts)
│   ├── crypto.py           # Token generation utilities
│   ├── database.py         # Primary database operations
│   ├── main.py             # **MAIN FASTAPI ENTRY POINT**
│   ├── requirements.txt    # Python dependencies
│   ├── test_api.py         # API integration tests
│   ├── test_schemas.py     # Schema validation tests
│   └── Dockerfile          # Backend Dockerfile
├── frontend/               # React/Vite frontend application
│   ├── public/             # Static assets
│   │   ├── assets/icons/   # Icon assets
│   │   ├── manifest.json   # PWA manifest
│   │   ├── offline.html    # PWA offline page
│   │   ├── nuru-icon.svg   # App icon
│   │   └── service_worker.js # PWA service worker
│   ├── src/
│   │   ├── api/            # API client utilities
│   │   │   ├── apiClient.js # Axios API client
│   │   │   └── health.js   # Health check utilities
│   │   ├── components/     # Reusable React components
│   │   │   ├── ui/         # ShadCN UI components (accordion, button, etc.)
│   │   │   ├── layout/     # Layout components (Navbar, Footer, AppLayout)
│   │   │   ├── landing/    # Landing page sections
│   │   │   ├── intake/     # Intake form step components
│   │   │   ├── nurse/      # Nurse-specific components
│   │   │   ├── ConnectionStatus.jsx
│   │   │   ├── LanguageSwitcher.jsx
│   │   │   ├── OfflineBanner.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── UserNotRegisteredError.jsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   └── use-mobile.jsx
│   │   ├── pages/          # Page components
│   │   │   ├── Landing.jsx
│   │   │   ├── RoleSelection.jsx
│   │   │   ├── FemaleIntake.jsx
│   │   │   ├── MaleDashboard.jsx
│   │   │   ├── PartnerSync.jsx
│   │   │   ├── SessionKey.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── SignUp.jsx
│   │   │   ├── Education.jsx
│   │   │   └── nurse/      # Nurse dashboard pages
│   │   ├── utils/
│   │   │   └── index.ts
│   │   ├── App.jsx         # Main app component
│   │   ├── main.jsx        # Frontend entry point
│   │   └── index.css       # Global styles
│   ├── .env.development    # Dev environment variables
│   ├── .env.production     # Prod environment variables
│   ├── .gitignore
│   ├── eslint.config.js    # ESLint config
│   ├── index.html
│   ├── package.json        # NPM dependencies
│   ├── package-lock.json
│   ├── postcss.config.mjs  # PostCSS config
│   ├── tailwind.config.js  # Tailwind config
│   ├── vite.config.js      # Vite config (duplicate)
│   ├── vite.config.mjs     # Vite config (primary)
│   └── README.md
├── data/                   # Datasets & synthetic profiles
│   ├── data/processed/     # Processed survey data from Kenya
│   ├── knowledge_base/     # RAG knowledge base (myths, WHO guidelines, etc.)
│   ├── processing/         # Data extraction/processing scripts
│   ├── dataset_extraction_log.md
│   ├── myths_complete.json
│   ├── method_benefits.json
│   └── README.md
├── docs/                   # Project documentation
│   ├── ai_logic_flow.md
│   ├── api_documentation.md
│   ├── clinical_validation.md
│   ├── deployment_guide.md
│   ├── ethics.md
│   ├── ethics_statement.md
│   ├── reproducibility_guide.md
│   └── setup_guide.md
├── notebooks/              # Jupyter notebooks for data exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_who_mec_mapping.ipynb
│   ├── 03_synthetic_generation.ipynb
│   └── 04_validation.ipynb
├── tests/                  # Integration & system tests
│   ├── edge_cases/
│   ├── integration/
│   ├── sync/
│   ├── test_api.py
│   ├── test_guardrails.py
│   └── test_safety_rules.py
├── .github/workflows/
│   └── ci.yml              # GitHub Actions CI/CD pipeline
├── .env.example            # Example environment variables
├── .gitignore
├── .dockerignore
├── Dockerfile              # Multi-stage Docker build (app + frontend)
├── docker-compose.yml      # Docker Compose orchestration
├── nginx.conf              # Nginx configuration for frontend
├── recreate_db.py          # Database reset script
├── recreate_tables.py      # Table recreation script
├── fix_environment.py      # Environment fix script
├── pytest.ini              # Pytest config
├── LICENSE                 # MIT License
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── Comprehensive Project Audit and Recommendations.md
└── README.md               # This file
```

## Core Module Breakdown

### Backend Modules
| Module | Key Files | Purpose |
|--------|-----------|---------|
| **API Endpoints** | `backend/main.py`, `backend/api/endpoints/` | Define REST API routes for intake, recommendations, sync, nurse auth |
| **Database Layer** | `backend/database.py`, `backend/db/schema.sql` | PostgreSQL/Supabase ORM & operations; stores profiles, nurse sessions, partner sync tokens |
| **Recommendation Engine** | `backend/engine/`, `backend/ai_client.py` | WHO MEC guardrails + AI (Gemini) recommendations |
| **Auth & Security** | `backend/auth.py`, `backend/crypto.py`, `backend/sync/partner_sync.py` | JWT tokens, nurse login, partner sync tokens |
| **RAG Knowledge Base** | `backend/engine/rag_pipeline.py`, `data/knowledge_base/` | Retrieves educational content, myths, WHO guidelines for recommendations |

### Frontend Pages & Components
| Page | Path | Purpose |
|------|------|---------|
| Landing Page | `/` | Intro, features, CTA |
| Role Selection | `/role` | Choose patient/nurse |
| Female Intake | `/intake` | 8-step health questionnaire |
| Male Dashboard | `/male-dashboard` | Male partner interface |
| Partner Sync | `/sync` | Generate/verify partner sync tokens |
| Session Key | `/session-key` | Generate nurse access keys |
| Nurse Login | `/nurse/login` | Nurse authentication |
| Nurse Dashboard | `/nurse/dashboard` | Nurse patient lookup & analytics |
| Education | `/education` | Educational content about contraceptives |

---

## Quick Start with Docker (Recommended)

This is the easiest way to get NuruCare up and running!

### Prerequisites
- Docker
- Docker Compose

---

## Comprehensive Docker Operations Guide

### 1. Initial Setup & First Run

#### Step 1: Clone the repository
```bash
git clone <repository-url>
cd nurucare
```

#### Step 2: Set up environment variables
```bash
# Copy the example env file to .env
cp .env.example .env

# Optional: Edit .env to add your API keys (GEMINI_API_KEY, SUPABASE_URL, etc.)
# For example, on Windows you can use notepad:
notepad .env
```

#### Step 3: Build and start all services
```bash
# Build images and start containers in detached mode (in background)
docker-compose up --build -d

# OR build and start in attached mode (see logs in terminal)
docker-compose up --build
```

### 2. Access the Application
Once containers are running, access services at:
- **Frontend**: http://localhost:3000 (mapped from 80 internally to avoid port conflicts)
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/health

---

### 3. Managing Containers

#### Start existing containers (without rebuilding)
```bash
# Start all services in detached mode
docker-compose up -d
```

#### Stop running containers
```bash
# Stop all containers but keep them (can be restarted later)
docker-compose stop

# OR stop and remove containers, networks and volumes (CAUTION: removes data)
docker-compose down
```

#### Restart containers
```bash
# Restart all services
docker-compose restart

# Restart a specific service (e.g., backend)
docker-compose restart app
```

#### View container status
```bash
# List all containers and their status
docker-compose ps

# OR use regular docker to list all containers
docker ps -a
```

---

### 4. Viewing Logs

#### View logs for all services
```bash
# View all logs
docker-compose logs

# View logs and follow (stream new logs)
docker-compose logs -f

# View last N lines of logs (e.g., last 100)
docker-compose logs --tail=100
```

#### View logs for a specific service
```bash
# View logs for backend (app)
docker-compose logs -f app

# View logs for frontend
docker-compose logs -f frontend

# View logs for database
docker-compose logs -f db
```

---

### 5. Accessing Container Shells

#### Open interactive shell in backend container
```bash
# Open a bash shell in the backend container
docker-compose exec app bash

# OR if bash isn't available, use sh
docker-compose exec app sh
```

#### Open interactive shell in database container
```bash
# Open bash shell in PostgreSQL container
docker-compose exec db bash
```

#### Access PostgreSQL database directly
```bash
# Connect to PostgreSQL using psql (from within db container)
docker-compose exec db psql -U nurucare -d nurucare

# OR run a single SQL command (e.g., check partner_sync table schema)
docker-compose exec db psql -U nurucare -d nurucare -c "\d partner_sync"
```

---

### 6. Troubleshooting Common Issues

#### Issue: Port already in use
If you get an error like `port is already allocated`, check which process is using the port:
```bash
# On Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# On macOS/Linux:
lsof -ti :3000 | xargs kill -9
lsof -ti :8000 | xargs kill -9
```

#### Issue: Database schema missing "used" column (partner_sync table)
If you get an error that column "used" doesn't exist:
```bash
# Add the column manually
docker-compose exec db psql -U nurucare -d nurucare -c "ALTER TABLE partner_sync ADD COLUMN IF NOT EXISTS used BOOLEAN NOT NULL DEFAULT FALSE;"
```

#### Issue: Containers won't start (dependency errors)
Try rebuilding all images from scratch:
```bash
# Stop and remove all containers/volumes/images
docker-compose down -v --rmi all

# Rebuild and start fresh
docker-compose up --build -d
```

#### Issue: Can't access the app from another device
If you want to access the app from another device on your network, ensure your firewall allows inbound connections on ports 3000 and 8000 and use your machine's local IP address instead of `localhost`.

---

### 7. Cleanup Operations

#### Remove all containers and networks
```bash
docker-compose down
```

#### Remove containers, networks and volumes (DATA LOSS WARNING)
This will delete all database data:
```bash
docker-compose down -v
```

#### Remove unused Docker resources
```bash
# Remove stopped containers, unused networks and dangling images
docker system prune

# Remove all unused images, not just dangling ones
docker system prune -a
```

---

### 8. Development Workflow with Docker

#### Rebuild a single service after code changes
```bash
# Rebuild just the backend after making changes to backend code
docker-compose up -d --no-deps --build app

# Rebuild just the frontend
docker-compose up -d --no-deps --build frontend
```

#### Run backend tests in Docker
```bash
# Run pytest inside the backend container
docker-compose exec app pytest
```

---

## Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- PostgreSQL (or use Docker for DB only)

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt

# Create a .env file in backend/ directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install

# Create a .env file with VITE_API_URL=http://localhost:8000
npm run dev
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT tokens | `nurucare-dev-secret-change-in-production` |
| `VITE_API_URL` | Backend API URL for frontend | `http://localhost:8000` |
| `DATABASE_URL` | PostgreSQL database URL | `postgresql://nurucare:nurucare@db:5432/nurucare` |
| `STORAGE_BACKEND` | Database backend (`local` or `supabase`) | `local` |
| `SUPABASE_URL` | Supabase project URL | - |
| `SUPABASE_KEY` | Supabase service role key | - |
| `GEMINI_API_KEY` | Google Gemini API key for AI recommendations | - |

## Team

| Role | Name |
|-------|------------|
| AI Lead + Coordinator | Brian Odhiambo Ouma |
| Backend + AI Integration | Alois Karanja Gitau |
| Frontend/UI Developer | Lisa Adongo Akinyi |
| Full Stack + Deployment | Uvyne Chepchirchir Rop |
| Health Expert + QA | Moffat Mose |

## License

MIT License

## Acknowledgments

- WHO MEC Guidelines (2024)
- Data Science Africa 2026 Hackathon
