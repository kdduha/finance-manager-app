from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

import src.db as db
import src.errors as errors
from src.auth import auth
from src.schemas.base import DELETE_MODEL_RESPONSE
from src.schemas.users import User, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses=errors.error_responses(
        errors.NotFoundException,
        errors.ValidationException,
        errors.AuthorizationException,
    ),
)


@router.get("/", summary="Get a list of all users.", response_model=list[User])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    users = session.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", summary="Get the User by id.", response_model=User)
async def get_user(
    user_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    return user


@router.put("/{user_id}", summary="Update the User Info by id.", response_model=User)
async def update_user(
    user_id: int,
    request: UserUpdate,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    request.custom_validate(birth_date=request.birth_date)

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(user, key, value)

    session.commit()
    session.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    summary="Delete the User by id.",
    responses={status.HTTP_200_OK: DELETE_MODEL_RESPONSE},
)
async def delete_user(
    user_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    session.delete(user)
    session.commit()

    return {"detail": f"User with id {user_id} has been deleted."}
