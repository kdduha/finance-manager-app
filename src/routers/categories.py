from fastapi import APIRouter, Query
from typing import List
from ..schemas.categories import *

import src.utils.errors as errors

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses=errors.NOT_FOUND_RESPONSE,
)

fake_categories_db = {}


@router.post("/", summary="Create a new Category.", response_model=CategoryResponse)
async def create_category(request: CategoryCreateRequest):
    category_id = len(fake_categories_db) + 1
    new_category = {
        "id": category_id,
        "user_id": request.user_id,
        "name": request.name,
        "type": request.type,
    }
    fake_categories_db[category_id] = new_category
    return new_category


@router.get("/{category_id}", summary="Get the Category by id.", response_model=CategoryResponse)
async def get_category(category_id: int):
    category = fake_categories_db.get(category_id)

    errors.handle_not_found_error(
        entity_id=category_id,
        entity_name="Category",
        entity=category,
    )

    return category


@router.get("/", summary="List the Category.", response_model=List[CategoryResponse])
async def list_category(
        user_id: str | None = Query(None, description="Filter by User ID"),
        name: str | None = Query(None, description="Filter by Category Name"),
        cat_type: CategoryType | None = Query(None, description="Filter by Category Type")
):
    filtered_categories = []
    for category in fake_categories_db.values():
        if user_id and user_id != category["user_id"]:
            continue
        if name and name.lower() not in category["name"].lower():
            continue
        if cat_type and cat_type != category["type"]:
            continue
        filtered_categories.append(category)

    return filtered_categories


@router.put("/{category_id}", summary="Update the Category by id.", response_model=CategoryResponse)
async def update_category(category_id: int, request: CategoryUpdateRequest):
    category = fake_categories_db.get(category_id)

    errors.handle_not_found_error(
        entity_id=category_id,
        entity_name="Category",
        entity=category,
    )

    updated_data = request.model_dump(exclude_unset=True)
    category.update(updated_data)

    fake_categories_db[category_id] = category
    return category


@router.delete("/{category_id}", summary="Delete the Category by id.")
async def delete_user(category_id: int):
    category = fake_categories_db.get(category_id)

    errors.handle_not_found_error(
        entity_id=category_id,
        entity_name="Category",
        entity=category,
    )

    del fake_categories_db[category_id]
    return {}
