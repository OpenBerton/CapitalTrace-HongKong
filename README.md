# CCASS Chip Analyzer

English version: [README.en.md](README.en.md)

港股 CCASS 主力籌碼分析網站，採用前後端分離架構。
後端以 FastAPI 即時抓取 HKEX CCASS 資料並進行整理，前端使用 React + Vite 呈現券商持倉分佈、持倉變化與集中度摘要。

## 專案簡介

本專案聚焦於「單一股票、單一交易日」的籌碼觀察，主要提供：

- 前二十大券商持倉與佔比
- 持倉變化（股數）與相對前一天變化率（%）
- 自訂勾選券商的淨流入/流出統計
- 兩階段資料載入（先快、後補全）以改善體感速度

## 資料口徑

- 查詢日期（T）：使用者選擇的有效港股交易日
- CCASS 交收日期（T+2）：顯示於 `ccass_settlement_date`
- 變化比較基準（T+1）：用來計算 `deltaShares` 與變化率
- 前端日期選擇已限制在可用區間（避免查到尚未公布的 T+2）

## 功能亮點

- 後端快取與啟動暖身：降低首次請求延遲
- enriched 端點補強：補上收盤價與持倉變化，不阻塞基礎結果
- duplicate-name 安全匹配：優先以 `participantId` 比對，降低同名機構誤配風險
- SPA + API 同服務：後端可同時提供 API 與前端靜態檔

## API 概覽

- `GET /api/v1/chips`
  - 回傳基礎籌碼資料（快速）
- `GET /api/v1/chips/enriched`
  - 回傳補強資料（含收盤價、delta）
- `GET /api/v1/trading-days`
  - 回傳可用交易日清單
- `GET /healthz`
  - 服務健康檢查

## 專案結構

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

## 安裝指南

先進入專案根目錄（也就是包含 `backend/` 與 `frontend/` 的資料夾）。

### macOS / Linux

1. 安裝後端依賴

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 安裝前端依賴

```bash
cd frontend
npm install
```

### Windows

1. 安裝後端依賴（PowerShell）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. 安裝後端依賴（Command Prompt）

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

3. 安裝前端依賴

```powershell
cd frontend
npm install
```

> 如果你的系統尚未安裝 Node.js，請先安裝 Node.js / npm。

## 啟動服務

### macOS / Linux

1. 啟動後端 API

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. 開啟新終端，啟動前端

```bash
cd frontend
npm run dev
```

3. 在瀏覽器打開

```text
http://localhost:5173
```

### Windows

1. 啟動後端 API（PowerShell）

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. 啟動後端 API（Command Prompt）

```bat
cd backend
.venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. 開啟新終端，啟動前端

```powershell
cd frontend
npm run dev
```

4. 在瀏覽器打開

```text
http://localhost:5173
```

## 健康檢查

如果要確認後端是否成功啟動，測試：

```text
http://localhost:8000/healthz
```
