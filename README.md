# CCASS Chip Analyzer

港股 CCASS 主力籌碼即時分析網站，採用前後端分離的無狀態架構。後端透過 FastAPI 即時爬取 CCASS 原始頁面，前端使用 React、Vite 與 Tailwind 渲染籌碼圖表。

## 專案結構

- `backend/`
  - `app/`
    - `controllers/`
    - `services/`
    - `schemas/`
    - `utils/`
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

## 安裝指南

### 後端

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 前端

```bash
cd frontend
npm install
```

> 如果你的系統尚未安裝 Node.js，請先安裝 Node.js / npm。

## 啟動服務

### macOS

1. 啟動後端

```bash
cd /Users/bertonkhw/Desktop/CapitalTrace/backend
. .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. 開啟新終端，啟動前端

```bash
cd /Users/bertonkhw/Desktop/CapitalTrace/frontend
npm install
npm run dev
```

3. 在瀏覽器打開

```text
http://localhost:5173
```

### Windows

1. 後端

```powershell
cd C:\Users\<your-user>\Desktop\CapitalTrace\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. 前端

```powershell
cd C:\Users\<your-user>\Desktop\CapitalTrace\frontend
npm install
npm run dev
```

3. 在瀏覽器打開

```text
http://localhost:5173
```

## 健康檢查

如果要確認後端是否成功啟動，測試：

```text
http://localhost:8000/healthz
```
