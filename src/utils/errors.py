from pydantic import BaseModel
from fastapi import HTTPException
from typing import Any


class BaseError(BaseModel):
    detail: str


NOT_FOUND_CODE: int = 404

NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {NOT_FOUND_CODE: {"model": BaseError}}


def handle_not_found_error(entity_id: int, entity_name: str, entity: BaseModel | None) -> None:
    if not entity:
        raise HTTPException(
            status_code=NOT_FOUND_CODE,
            detail=f"{entity_name} <{entity_id}> not found."
        )
