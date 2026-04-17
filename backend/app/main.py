from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.controllers.chip_controller import router as chip_router
from app.core.exceptions import CCASSNotFoundError, CCASSParseError, CCASSServiceError
from app.services.ccass_service import warm_ccass_form_cache
from app.services.trading_day_service import warm_trading_days_cache

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

app = FastAPI(
    title="CCASS Chip Analyzer",
    version="0.1.0",
    description="港股 CCASS 主力籌碼即時分析 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chip_router, prefix="/api/v1")


@app.on_event("startup")
async def warmup_ccass_metadata() -> None:
    await warm_ccass_form_cache()
    await warm_trading_days_cache()


@app.get("/", include_in_schema=False)
async def serve_spa_root() -> FileResponse:
    return FileResponse(FRONTEND_DIST / "index.html")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    requested_file = FRONTEND_DIST / full_path
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(requested_file)
    return FileResponse(FRONTEND_DIST / "index.html")


@app.exception_handler(CCASSNotFoundError)
def ccass_not_found_exception_handler(request: Request, exc: CCASSNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(CCASSParseError)
def ccass_parse_exception_handler(request: Request, exc: CCASSParseError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(TimeoutError)
def timeout_exception_handler(request: Request, exc: TimeoutError) -> JSONResponse:
    return JSONResponse(status_code=504, content={"detail": str(exc)})


@app.exception_handler(CCASSServiceError)
def ccass_service_exception_handler(request: Request, exc: CCASSServiceError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ccass-chip-analyzer"}
