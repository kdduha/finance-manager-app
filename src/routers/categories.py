from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

import src.db as db
import src.errors as errors
from src.auth import auth
from src.schemas.base import DELETE_MODEL_RESPONSE
from src.schemas.categories import (
    Category,
    CategoryDefault,
    CategoryType,
    CategoryUpdate,
)
from src.schemas.users import User

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses=errors.error_responses(
        errors.NotFoundException,
        errors.ValidationException,
        errors.AuthorizationException,
    ),
)


@router.post("/", summary="Create a new Category.", response_model=Category)
async def create_category(
    request: CategoryDefault,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    request.custom_validate(type=request.type)

    user = session.get(User, request.user_id)
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    category = Category(**request.dict())

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


@router.get("/{category_id}", summary="Get the Category by id.", response_model=Category)
async def get_category(
    category_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    category = session.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    return category


@router.get("/", summary="List the Category.", response_model=list[Category])
async def list_category(
    user_id: str | None = Query(None, description="Filter by User ID"),
    name: str | None = Query(None, description="Filter by Category Name"),
    cat_type: CategoryType | None = Query(None, description="Filter by Category Type"),
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    query = session.query(Category)

    if user_id:
        query = query.filter(Category.user_id == user_id)
    if name:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    if cat_type:
        query = query.filter(Category.type == cat_type)

    categories = query.all()
    return categories


@router.put("/{category_id}", summary="Update the Category by id.", response_model=Category)
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    category = session.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(category, key, value)

    session.commit()
    session.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    summary="Delete the Category by id.",
    responses={status.HTTP_200_OK: DELETE_MODEL_RESPONSE},
)
async def delete_user(
    category_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    category = session.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    session.delete(category)
    session.commit()

    return {"detail": f"Category with id {category_id} has been deleted."}
