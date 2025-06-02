from fastapi import APIRouter, Depends

import src.errors as errors
from celery.result import AsyncResult
from src.auth import auth
from src.celery import celery_app, parse_url_task
from src.config import cfg
from src.schemas.parser import (
    ParseRequest,
    ParseResult,
    TaskStatusResponse,
)

router = APIRouter(
    prefix="/parser",
    tags=["Parser"],
    responses=errors.error_responses(
        errors.AuthorizationException,
        errors.BadRequestException,
        errors.NotFoundException,
    ),
)


@router.post("/parse", summary="Launch Async parsing of posts")
def start_parsing(
    req: ParseRequest,
    _=Depends(auth.get_current_user),
):
    if not cfg.parser.enabled:
        raise errors.BadRequestException(detail="Parser functionality is disabled")

    task = parse_url_task.delay(req.count)
    return {"task_id": task.id, "message": "Parsing started"}


@router.get("/task/{task_id}", response_model=TaskStatusResponse, summary="Get parsing status")
def get_task_status(
    task_id: str,
    _=Depends(auth.get_current_user),
):
    if not cfg.parser.enabled:
        raise errors.BadRequestException(detail="Parser functionality is disabled")

    result = AsyncResult(task_id, app=celery_app)

    if result.failed():
        exc = result.result
        raise errors.BadRequestException(detail=exc.detail)

    data = None
    if result.successful():
        data = ParseResult.parse_obj(result.result)

    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=data,
    )
