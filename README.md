# NuruCare

## AI-Powered Contraceptive Decision-Support Platform for Sub-Saharan Africa

> *"Nuru" means "Light" in Swahili — illuminating informed contraceptive choices.*

## Overview

NuruCare is an ethical, explainable AI platform that helps individuals in Sub-Saharan Africa make safer, personalized, and informed contraceptive choices based on their health profiles, preferences, and reproductive goals.

## Features

- ✅ **Intelligent Intake Form** - 8 health questions
- ✅ **WHO MEC Safety Rules** - Clinical guardrails
- ✅ **RAG + Gemini Flash** - Personalized recommendations
- ✅ **Multilingual** - English + Swahili
- ✅ **Offline Capable** - PWA with service workers
- ✅ **Privacy First** - Cryptographic sync tokens, 15-min nurse keys

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Tailwind CSS + PWA |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + Supabase |
| AI | Gemini Flash API + pgvector |
| Deployment | Docker + Docker Compose |

## Project Structure

```
nurucare/
├── backend/       # FastAPI backend
├── frontend/      # React frontend
├── data/          # Datasets + synthetic profiles
├── notebooks/     # Jupyter notebooks
├── docs/          # Documentation
├── tests/         # Unit tests
├── .github/       # CI/CD workflows
├── Dockerfile     # Multi-stage Docker build
├── docker-compose.yml  # Docker orchestration
└── nginx.conf     # Nginx configuration for static files
```

## Quick Start with Docker

This is the easiest way to get NuruCare up and running!

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nurucare
   ```

2. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```
   Optional: Edit `.env` to add your API keys (GEMINI_API_KEY, SUPABASE_URL, etc.)

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/health

5. **Stop services**:
   ```bash
   docker-compose down
   ```

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
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create a backend .env file with your configuration
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
