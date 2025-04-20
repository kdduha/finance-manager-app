from typing import Any, ClassVar, Type, Union

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette import status

# === Custom Errors ===


class NotFoundException(Exception):
    status: ClassVar[int] = status.HTTP_404_NOT_FOUND
    detail: str

    def __init__(self, entity_name: str, entity_id: int):
        self.detail = f"{entity_name} <{entity_id}> not found."

    def json(self) -> JSONResponse:
        return JSONResponse(status_code=self.status, content={"detail": self.detail})

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Entity not found",
                "content": {"application/json": {"example": {"detail": "string"}}},
            }
        }


class ValidationExceptionDetail(BaseModel):
    loc: list[Union[str, int]]
    msg: str
    type: str


class ValidationException(Exception):
    status: ClassVar[int] = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail: ValidationExceptionDetail

    def __init__(self, errors: ValidationExceptionDetail):
        self.detail = errors

    def json(self) -> JSONResponse:
        return JSONResponse(status_code=self.status, content={"detail": self.detail.dict()})

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "loc": ["body", "string"],
                                "msg": "string",
                                "type": "Type[]",
                            }
                        }
                    }
                },
            }
        }


class AuthorizationException(Exception):
    status: ClassVar[int] = status.HTTP_401_UNAUTHORIZED
    detail: str

    def __init__(self, detail: str):
        self.detail = detail

    def json(self) -> JSONResponse:
        return JSONResponse(status_code=self.status, content={"detail": self.detail})

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Authorization error",
                "content": {"application/json": {"example": {"detail": "string"}}},
            }
        }


class BadRequestException(Exception):
    status: ClassVar[int] = status.HTTP_400_BAD_REQUEST
    detail: str

    def __init__(self, detail: str):
        self.detail = detail

    def json(self) -> JSONResponse:
        return JSONResponse(status_code=self.status, content={"detail": self.detail})

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Bad request error",
                "content": {"application/json": {"example": {"detail": "string"}}},
            }
        }


# === Errors Handlers ===


async def validation_exception_handler(_: Request, exc: ValidationException):
    return exc.json()


async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return exc.json()


async def authorization_exception_handler(_: Request, exc: AuthorizationException):
    return exc.json()


async def bad_request_exception_handler(_: Request, exc: AuthorizationException):
    return exc.json()


# === Utils ===


def error_responses(*errors: Type[Exception]) -> dict[int, dict[str, Any]]:
    responses = {}
    for error in errors:
        responses.update(error.response())
    return responses
