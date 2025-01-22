from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from typing import Any, Optional

class Ok:
    def __init__(self, data: Optional[Any] = None, message: Optional[str] = None) -> None:
        self.message = message
        self.data = data or {}

    def json(self):
        return JSONResponse(content={"status": "success", "message": self.message, "data": self.data}, status_code=status.HTTP_200_OK)

class Created:
    def __init__(self, data: Optional[Any] = None) -> None:
        self.data = data or {}

    def json(self):
        return JSONResponse(content={"status": "success", "data": self.data}, status_code=status.HTTP_201_CREATED)

class NotFound:
    def __init__(self, message: str = "Not Found") -> None:
        self.message = message

    def http_exception(self):
        raise HTTPException(
            detail={"status": "error", "message": self.message},
            status_code=status.HTTP_404_NOT_FOUND
        )

class BadRequest:
    def __init__(self, message: str = "Bad Request", errors: Optional[dict] = None) -> None:
        self.message = message
        self.errors = errors or {}

    def http_exception(self):
        raise HTTPException(
            detail={"status": "error", "message": self.message, "errors": self.errors},
            status_code=status.HTTP_400_BAD_REQUEST
        )

class Forbidden:
    def __init__(self, message: str = "Forbidden") -> None:
        self.message = message

    def http_exception(self):
        raise HTTPException(
            detail={"status": "error", "message": self.message},
            status_code=status.HTTP_403_FORBIDDEN
        )

class Unauthorized:
    def __init__(self, message: str = "Unauthorized") -> None:
        self.message = message

    def http_exception(self):
        raise HTTPException(
            detail={"status": "error", "message": self.message},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class InternalServerError:
    def __init__(self, error: str = "Internal Server Error") -> None:
        self.error = error

    def http_exception(self):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": self.error}
        )