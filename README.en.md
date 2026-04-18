# CCASS Chip Analyzer

A real-time Hong Kong CCASS major holding analysis web app with a stateless frontend-backend architecture. The backend uses FastAPI to fetch CCASS source pages in real time, while the frontend uses React, Vite, and Tailwind to render charts and holding insights.

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
