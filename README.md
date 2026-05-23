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
| Deployment | Vercel / Render |

## Project Structure
nurucare/
├── backend/ # FastAPI backend
├── frontend/ # React frontend
├── data/ # Datasets + synthetic profiles
├── notebooks/ # Jupyter notebooks
├── docs/ # Documentation
├── tests/ # Unit tests
├── .github/ # CI/CD workflows
└── pitch/ # Presentation materials


## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
cd frontend
npm install
npm run dev

### Team
| Role | Name |
|-------|------------|
| AI Lead + Coordinator | Brian Odhiambo Ouma |
| Backend + AI Integration | Alois Karanja Gitau |
| Frontend/UI Developer | Lisa Adongo Akinyi |
| Full Stack + Deployment | Uvyne Chepchirchir Rop |
| Health Expert + QA | Moffat Mose |

### License
MIT License

### Acknowledgments
WHO MEC Guidelines (2024)

Data Science Africa 2026 Hackathon
