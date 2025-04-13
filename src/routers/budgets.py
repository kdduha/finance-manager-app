from fastapi import APIRouter, Query
from typing import List

from ..schemas.budget import *
from ..schemas.transactions import *

from datetime import datetime

import src.utils.errors as errors

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
    responses=errors.NOT_FOUND_RESPONSE,
)

fake_budgets_db = {}


@router.post("/", summary="Create a new Budget.", response_model=BudgetResponse)
async def create_budget(request: BudgetCreateRequest):
    budget_id = len(fake_budgets_db) + 1
    new_budget = {
        "id": budget_id,
        "user_id": request.user_id,
        "category_id": request.category_id,
        "limit_amount": request.limit_amount,
        "start_date": datetime.utcnow(),
        "end_date": request.end_date,
    }
    fake_budgets_db[budget_id] = new_budget
    return new_budget


@router.get("/{budget_id}", summary="Get the Budget by id.", response_model=BudgetResponse)
async def get_budget(budget_id: int):
    budget = fake_budgets_db.get(budget_id)

    errors.handle_not_found_error(
        entity_id=budget_id,
        entity_name="Budget",
        entity=budget,
    )

    return budget


@router.get("/", summary="List the Budget.", response_model=List[BudgetResponse])
async def list_budget(
        user_id: str | None = Query(None, description="Filter by User ID"),
        category_id: str | None = Query(None, description="Filter by Category ID"),
):
    filtered_budgets = []
    for budget in fake_budgets_db.values():
        if user_id and user_id != fake_budgets_db["user_id"]:
            continue
        if category_id and category_id != fake_budgets_db["category_id"].lower():
            continue
        filtered_budgets.append(budget)

    return filtered_budgets


@router.put("/{budget_id}", summary="Update the Budget by id.", response_model=BudgetResponse)
async def update_budget(budget_id: int, request: BudgetUpdateRequest):
    budget = fake_budgets_db.get(budget_id)

    errors.handle_not_found_error(
        entity_id=budget_id,
        entity_name="Budget",
        entity=budget,
    )

    updated_data = request.model_dump(exclude_unset=True)
    budget.update(updated_data)

    fake_budgets_db[budget_id] = budget
    return budget


@router.delete("/{budget_id}", summary="Delete the Budget by id.")
async def delete_budget(budget_id: int):
    budget = fake_budgets_db.get(budget_id)

    errors.handle_not_found_error(
        entity_id=budget_id,
        entity_name="Budget",
        entity=budget,
    )

    del fake_budgets_db[budget_id]
    return {}


@router.get("/{budget_id}/transactions", summary="Get all transactions below the Budget.", response_model=List[TransactionResponse])
async def list_transactions_below_budget(budget_id: int):
    # NOT IMPLEMENTED
    return [{"id": 0, "user_id": 0, "category_id": 0, "amount": 0.2, "date": "2023-12-23", "description": "fake"}]