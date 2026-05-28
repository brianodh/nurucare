# NuruCare Backend - Setup Guide

## Author: Alois Gitau
## Date: May 2026

---

## Prerequisites

- Python 3.10 or higher
- Git
- VS Code or any text editor

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/brianodh/nurucare
cd care_nuru

2. Create Virtual Environment
bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Create .env File
bash
cat > .env << 'EOF'
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key
ENVIRONMENT=development
EOF
5. Run API
bash
uvicorn main:app --reload
6. Test
Open browser: http://localhost:8000/health

Troubleshooting
Problem	Solution
Port 8000 busy	fuser -k 8000/tcp
Module not found	pip install -r requirements.txt
Invalid API key	Check .env file
Team URLs
API: http://localhost:8000

Docs: http://localhost:8000/docs

Health: http://localhost:8000/health

Contact: Alois Gitau

text

---

# FILE 2: `api_endpoints_design.md` — Copy EVERYTHING below

```markdown
# NuruCare API Endpoints Design

**Author:** Alois Karanja Gitau | **Date:** May 28, 2026

## Base URL: `http://localhost:8000`

## All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/api/v1/intake` | Submit health data |
| POST | `/api/v1/recommend` | Get contraceptive advice |
| POST | `/api/v1/session-key` | Generate nurse code |
| POST | `/api/v1/nurse/patient` | Nurse view patient |
| POST | `/api/v1/sync/token` | Generate partner token |
| POST | `/api/v1/sync/verify` | Verify partner token |
| POST | `/api/v1/translate` | Translate to Swahili |

---

## 1. GET `/`
```json
{"message": "NuruCare API is running", "status": "healthy", "version": "1.0.0"}
2. GET /health
json
{"status": "healthy", "timestamp": "2026-05-28T10:00:00"}
3. POST /api/v1/intake
Request:

json
{
  "age": 25,
  "gender": "female",
  "smoking": false,
  "migraine_type": "none",
  "fertility_intention": "long_term",
  "parity": 0
}
Response:

json
{"success": true, "session_id": "session_25_1234567890", "message": "Intake data received"}
4. POST /api/v1/recommend
Request: Same as intake

Response:

json
{
  "recommended_methods": [
    {"name": "Progestin-only Pill", "effectiveness": 93, "explanation": "Safe for your profile"},
    {"name": "Copper IUD", "effectiveness": 99, "explanation": "Long-acting, no hormones"}
  ],
  "restricted_methods": [],
  "requires_provider_consultation": false,
  "general_advice": "Consult a healthcare provider before starting any method.",
  "timestamp": "2026-05-28T10:00:00",
  "swahili_version": "Shauriana na daktari kabla ya kuanza njia yoyote."
}
5. POST /api/v1/session-key
Request: {"patient_id": "session_123"}

Response: {"session_key": "483729", "expires_in_minutes": 15}

6. POST /api/v1/nurse/patient
Request: {"session_key": "483729"}

Response: {"success": true, "patient_data": {"age": 28, "fertility_intention": "long_term"}}

7. POST /api/v1/sync/token
Request: None

Response: {"token": "abc123def456...", "expires_in_hours": 24}

8. POST /api/v1/sync/verify
Request: {"token": "abc123...", "your_id": "user_123"}

Response: {"success": true, "partner_id": "partner_456", "message": "Connected successfully"}

9. POST /api/v1/translate
Request: {"text": "Use condoms", "target_language": "swahili"}

Response: {"original": "Use condoms", "translated": "Tumia kondomu", "language": "swahili"}

Error Response
json
{"detail": "Error message here"}
Status Codes
Code	Meaning
200	Success
400	Bad request
401	Invalid key
500	Server error
WHO MEC Safety Rules
Condition	Action
Age < 20	Recommend condoms + POP
Age > 35 + Smoking	Block combined pills
Migraine with aura	Block combined pills
Breastfeeding	Recommend POP + LAM
High BP > 160	Block hormonal methods
Quick Test Commands
bash
# Health check
curl http://localhost:8000/health

# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommend -H "Content-Type: application/json" -d '{"age":25,"gender":"female","smoking":false,"migraine_type":"none","fertility_intention":"long_term","parity":0}'

# Get session key
curl -X POST http://localhost:8000/api/v1/session-key -H "Content-Type: application/json" -d '{"patient_id":"test"}'