# CourtGPT Auditor

An Explainable Multi-Agent AI Framework for Auditing Judicial Judgments and Legal Reasoning (Target Jurisdiction: India).

## Quickstart

### 1. Start Backend API
```bash
cd courtgpt-auditor
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn backend.app.api.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 2. Start Frontend UI
```bash
cd frontend
npm run dev
```
Open browser at: `http://localhost:5173`

### 3. Run Automated Tests
```bash
$env:PYTHONPATH = (Get-Location).Path
python -m pytest backend/tests/test_audit_suite.py -v
```

### 4. Docker Deployment
```bash
docker compose up --build
```
