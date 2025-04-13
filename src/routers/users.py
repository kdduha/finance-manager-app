from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..schemas.users import *

import src.utils.errors as errors

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses=errors.NOT_FOUND_RESPONSE,
)

fake_users_db = {}


@router.post("/", summary="Create a new User.")
async def create_user(request: UserCreateRequest):
    user_id = len(fake_users_db) + 1
    new_user = {
        "id": user_id,
        "username": request.username,
        "email": request.email,
        "birth_date": request.birth_date,
        "created_at": datetime.utcnow()
    }
    fake_users_db[user_id] = new_user
    return new_user


@router.get("/{user_id}", summary="Get the User by id.", response_model=UserResponse)
async def get_user(user_id: int):
    user = fake_users_db.get(user_id)

    errors.handle_not_found_error(
        entity_id=user_id,
        entity_name="User",
        entity=user,
    )

    return user


@router.put("/{user_id}", summary="Update the User Info by id.", response_model=UserResponse)
async def update_user(user_id: int, request: UserUpdateRequest):
    user = fake_users_db.get(user_id)

    errors.handle_not_found_error(
        entity_id=user_id,
        entity_name="User",
        entity=user,
    )

    updated_data = request.model_dump(exclude_unset=True)
    user.update(updated_data)

    fake_users_db[user_id] = user
    return user


@router.delete("/{user_id}", summary="Delete the User by id.")
async def delete_user(user_id: int):
    user = fake_users_db.get(user_id)

    errors.handle_not_found_error(
        entity_id=user_id,
        entity_name="User",
        entity=user,
    )

    del fake_users_db[user_id]
    return {}
