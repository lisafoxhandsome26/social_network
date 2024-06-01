from fastapi.exceptions import ValidationException
from httpx import Request
from starlette import status
from starlette.responses import JSONResponse

from backend.src.main import app


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content="some happen wrong please wait some minute, we try to fix"
    )
