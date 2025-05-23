from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

import src.db as db
import src.errors as errors
from src.auth import auth
from src.schemas.base import DELETE_MODEL_RESPONSE
from src.schemas.tags import Tag, TagDefault, TagUpdate
from src.schemas.users import User

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    responses=errors.error_responses(
        errors.NotFoundException,
        errors.ValidationException,
        errors.AuthorizationException,
    ),
)


@router.post("/", summary="Create a new Tag.", response_model=Tag)
async def create_tag(
    request: TagDefault,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    user = session.get(User, request.user_id)
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    tag = Tag(**request.dict())
    session.add(tag)
    session.commit()
    session.refresh(tag)

    return tag


@router.get("/{tag_id}", summary="Get the Tag by id.", response_model=Tag)
async def get_tag(
    tag_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise errors.NotFoundException(entity_name="Tag", entity_id=tag_id)
    return tag


@router.get("/", summary="List Tags.", response_model=list[Tag])
async def list_tags(
    user_id: int | None = Query(None, description="Filter by User ID"),
    name: str | None = Query(None, description="Filter by Tag Name"),
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    query = session.query(Tag)

    if user_id is not None:
        query = query.filter(Tag.user_id == user_id)
    if name:
        query = query.filter(Tag.name.ilike(f"%{name}%"))

    return query.all()


@router.put("/{tag_id}", summary="Update the Tag by id.", response_model=Tag)
async def update_tag(
    tag_id: int,
    request: TagUpdate,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise errors.NotFoundException(entity_name="Tag", entity_id=tag_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(tag, key, value)

    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", summary="Delete the Tag by id.", responses={status.HTTP_200_OK: DELETE_MODEL_RESPONSE})
async def delete_tag(
    tag_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise errors.NotFoundException(entity_name="Tag", entity_id=tag_id)

    session.delete(tag)
    session.commit()

    return {"detail": f"Tag with id {tag_id} has been deleted."}
