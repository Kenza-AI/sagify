from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, detail="Not Found"):
        super().__init__(status_code=404, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail="Internal Server Error"):
        super().__init__(status_code=500, detail=detail)


async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


async def internal_server_error_handler(request: Request, exc: InternalServerError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )
