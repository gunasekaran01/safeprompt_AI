# SafePrompt AI

**Prompt Injection and Toxicity Detection Platform**

SafePrompt AI is a full-stack AI safety application for detecting prompt
injection attempts, jailbreaks, and toxic content in user-submitted
prompts. It returns a safety score, risk level, recommendation, and
reasoning for every analyzed prompt, and surfaces trends through a
dashboard with history and reporting.

> This project is being built incrementally, milestone by milestone.
> See `PROGRESS.md` for current status.

## Project Structure

```
safeprompt-ai/
├── frontend/       React + Vite + Tailwind CSS dashboard
├── backend/        FastAPI + SQLAlchemy + AI detection services
├── datasets/       Sample/reference datasets for detection models
├── reports/        Generated PDF safety reports
└── README.md
```

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, React Router, Axios, Chart.js

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite

**AI:** Hugging Face Transformers, Detoxify, Sentence Transformers

**Deployment:** Docker

## Getting Started (Milestone 1)

At this stage, the project scaffold is in place: both apps install and run,
Tailwind styling works, and the backend exposes a health check endpoint.
Routing, pages, and detection logic are added in later milestones.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`, with interactive
Swagger docs at `http://localhost:8000/api/docs` and a health check at
`http://localhost:8000/api/health`.

> Note: `requirements.txt` includes heavier ML dependencies (torch,
> transformers, detoxify, sentence-transformers) that are used starting
> from Milestone 7 onward. Installing them now is optional for Milestone 1
> if you only want to verify the API boots — you can install a minimal
> subset (`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`,
> `SQLAlchemy`, `python-dotenv`) and add the rest later.

## Milestones

1. **Project setup** ✅
2. React routing
3. Landing page
4. Dashboard
5. Prompt Analyzer
6. Backend API
7. Prompt Injection Detector
8. Toxicity Detector
9. Safety Score Engine
10. SQLite database
11. History
12. Charts
13. PDF Report
14. Deployment
15. Documentation

## License

TBD.
