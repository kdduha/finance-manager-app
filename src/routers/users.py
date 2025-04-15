from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas.users import *
from src.schemas.base import DELETE_MODEL_RESPONSE
import src.utils.errors as errors
import src.db as db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses=errors.error_responses(
        errors.NotFoundException, errors.ValidationException,
    ),
)


@router.post("/", summary="Create a new User.", response_model=User)
async def create_user(request: UserDefault, session: Session = Depends(db.get_session)):

    user = User(**request.dict(), created_at=datetime.utcnow())
    user.custom_validate(birth_date=user.birth_date)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("/", summary="Get a list of all users.", response_model=list[User])
async def get_users(skip: int = 0, limit: int = 10, session: Session = Depends(db.get_session)):
    users = session.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", summary="Get the User by id.", response_model=User)
async def get_user(user_id: int, session: Session = Depends(db.get_session)):
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    return user


@router.put("/{user_id}", summary="Update the User Info by id.", response_model=User)
async def update_user(user_id: int, request: UserUpdate, session: Session = Depends(db.get_session)):
    request.custom_validate(birth_date=request.birth_date)

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(user, key, value)

    session.commit()
    session.refresh(user)

    return user


@router.delete("/{user_id}", summary="Delete the User by id.", responses={200: DELETE_MODEL_RESPONSE})
async def delete_user(user_id: int, session: Session = Depends(db.get_session)):
    user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=user_id)

    session.delete(user)
    session.commit()

    return {"detail": f"User with id {user_id} has been deleted."}

