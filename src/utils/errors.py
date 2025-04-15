from fastapi import Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Any, ClassVar, List, Union, Type


# === Custom Errors ===

class NotFoundException(Exception):
    status: ClassVar[int] = 404
    detail: str

    def __init__(self, entity_name: str, entity_id: int):
        self.detail = f"{entity_name} <{entity_id}> not found."

    def json(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": self.detail}
        )

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Entity not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "string"}
                    }
                }
            }
        }


class ValidationExceptionDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class ValidationException(Exception):
    status: ClassVar[int] = 422
    detail: ValidationExceptionDetail

    def __init__(self, errors: ValidationExceptionDetail):
        self.detail = errors

    def json(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": self.detail.dict()}
        )

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
                                "type": "Type[]"
                            }
                        }
                    }
                }
            }
        }


# === Errors Handlers ===

async def validation_exception_handler(_: Request, exc: ValidationException):
    return exc.json()


async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return exc.json()


# === Utils ===

def error_responses(*errors: Type[Exception]) -> dict[int, dict[str, Any]]:
    responses = {}
    for error in errors:
        responses.update(error.response())
    return responses





# gonna be deleted
def handle_not_found_error(entity_id: int, entity_name: str, entity: BaseModel | None) -> None:
    if not entity:
        error = NotFoundException(entity_name=entity_name, entity_id=entity_id)
        raise NotImplementedError
