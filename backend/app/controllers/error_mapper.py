from __future__ import annotations

from fastapi import HTTPException

from app.core.exceptions import CCASSNotFoundError, CCASSParseError


def map_chip_service_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, TimeoutError):
        return HTTPException(status_code=504, detail=str(exc))
    if isinstance(exc, ConnectionError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, CCASSNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, CCASSParseError):
        return HTTPException(status_code=502, detail=str(exc))
    raise exc


def map_trading_days_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, RuntimeError):
        return HTTPException(status_code=502, detail=str(exc))
    raise exc