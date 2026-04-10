from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers.chip_controller import router as chip_router
from app.core.exceptions import CCASSNotFoundError, CCASSParseError, CCASSServiceError

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
