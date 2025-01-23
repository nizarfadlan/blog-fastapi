from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app.core.config import Settings
from app.schemas.base import BaseResponse


def create_application(
    router: APIRouter,
    settings: Settings,
) -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
    )
    app.get("/")(lambda: {"message": "Welcome to the API"})

    app.include_router(router)

    app.mount("/static", StaticFiles(directory="uploads"), name="static")

    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    processed_errors = []
    for error in exc.errors():
        if "ctx" in error and "error" in error["ctx"] and isinstance(error["ctx"]["error"], ValueError):
            error["ctx"]["error"] = str(error["ctx"]["error"])
        processed_errors.append(error)

    custom_error_message = BaseResponse(
        status="error",
        message="Validation Error",
        errors=processed_errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=custom_error_message.model_dump(),
    )