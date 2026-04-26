# Hong Kong Capital Trace

Chinese version: [README.md](README.md)

A Hong Kong CCASS holding analysis web app built with a frontend-backend architecture.
The backend (FastAPI) fetches and normalizes HKEX CCASS data, while the frontend (React + Vite) visualizes participant holdings, concentration, and day-over-day changes.

## Overview

This project focuses on single-stock, single-date chip analysis with:

- Top 20 participant holdings and ratios
- Holding change in shares (`deltaShares`)
- Holding change rate (%) versus previous settlement day
- Custom selected-participant net flow summary
- Two-stage loading for better perceived performance (quick base result, then enriched result)

## Data Semantics

- Query date (T): user-selected valid HK trading day
- CCASS settlement date (T+2): returned as `ccass_settlement_date`
- Comparison baseline (T+1): used for `deltaShares` and change-rate calculation
- Frontend date picker is restricted to valid queryable dates

## Key Features

- Backend warmup + caching to reduce cold-start latency
- Enriched endpoint for close price and participant deltas
- Duplicate-name-safe matching (participant ID first)
- API and SPA served from the same backend service

## API Endpoints

- `GET /api/v1/chips`
  - Fast/base chip result
- `GET /api/v1/chips/enriched`
  - Enriched result (close price + deltas)
- `GET /api/v1/trading-days`
  - Valid trading-day list
- `GET /healthz`
  - Service health check

## Project Structure

- `backend/`
  - `app/`
    - `controllers/`
    - `services/`
    - `schemas/`
    - `utils/`
  - `scripts/`
  - `requirements.txt`
  - `.env`
- `frontend/`
  - `src/`
    - `api/`
    - `components/`
    - `hooks/`
    - `pages/`
    - `utils/`
  - `package.json`
  - `vite.config.js`
  - `tailwind.config.js`
  - `postcss.config.js`

## Installation

Start from the project root directory (the folder that contains both `backend/` and `frontend/`).

### macOS / Linux

1. Install backend dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install frontend dependencies

```bash
cd frontend
npm install
```

### Windows

1. Install backend dependencies (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Install backend dependencies (Command Prompt)

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

3. Install frontend dependencies

```powershell
cd frontend
npm install
```

> If Node.js is not installed on your machine, install Node.js and npm first.

## Run the App

### macOS / Linux

1. Start backend API

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open a new terminal and start frontend

```bash
cd frontend
npm run dev
```

3. Open in your browser

```text
http://localhost:5173
```

### Windows

1. Start backend API (PowerShell)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start backend API (Command Prompt)

```bat
cd backend
.venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Open a new terminal and start frontend

```powershell
cd frontend
npm run dev
```

4. Open in your browser

```text
http://localhost:5173
```

## Health Check

To verify the backend is running:

```text
http://localhost:8000/healthz
```
