from fastapi import APIRouter, Query
from typing import List
from ..schemas.transactions import *

import src.utils.errors as errors

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    responses=errors.NOT_FOUND_RESPONSE,
)

fake_transactions_db = {}

fake_categories_db = {
    1: {"id": 1, "user_id": 1, "name": "Еда", "type": "expense"},
    2: {"id": 2, "user_id": 1, "name": "Зарплата", "type": "income"},
}


@router.get("/with-details", summary="List Transactions with Category details.", response_model=List[TransactionWithCategoryResponse])
async def list_transactions_with_category_details():
    enriched_transactions = []

    for key, tx in fake_transactions_db.values():
        category = fake_categories_db.get(tx["category_id"])
        if not category:
            continue

        enriched_tx = {
            "id": key,
            **tx,
            "category": {
                "id": category["id"],
                "name": category["name"],
                "type": category["type"]
            }
        }
        enriched_transactions.append(enriched_tx)
        print(enriched_tx)

    return enriched_transactions



@router.post("/", summary="Create a new Transaction.", response_model=TransactionResponse)
async def create_transaction(request: TransactionCreateRequest):
    transaction_id = len(fake_transactions_db) + 1
    new_transaction = {
        "id": transaction_id,
        "user_id": request.user_id,
        "category_id": request.category_id,
        "amount": request.amount,
        "date": request.PastDate,
        "description": request.description,
    }
    fake_transactions_db[transaction_id] = new_transaction
    return new_transaction


@router.get("/{transaction_id}", summary="Get the Transaction by id.", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    transaction = fake_transactions_db.get(transaction_id)

    errors.handle_not_found_error(
        entity_id=transaction_id,
        entity_name="Transaction",
        entity=transaction,
    )

    return transaction


@router.get("/", summary="List the Transaction.", response_model=List[TransactionResponse])
async def list_transaction(
        user_id: str | None = Query(None, description="Filter by User ID"),
        category_id: str | None = Query(None, description="Filter by Category ID"),
        description: str | None = Query(None, description="Filter by Description")
):
    filtered_transactions = []
    for transaction in fake_transactions_db.values():
        if user_id and user_id != transaction["user_id"]:
            continue
        if category_id and category_id != transaction["category_id"].lower():
            continue
        if description and description.lower() not in transaction["description"].lower():
            continue
        filtered_transactions.append(transaction)

    return filtered_transactions


@router.put("/{transaction_id}", summary="Update the Transaction by id.", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, request: TransactionUpdateRequest):
    transaction = fake_transactions_db.get(transaction_id)

    errors.handle_not_found_error(
        entity_id=transaction_id,
        entity_name="Transaction",
        entity=transaction,
    )

    updated_data = request.model_dump(exclude_unset=True)
    transaction.update(updated_data)

    fake_transactions_db[transaction_id] = transaction
    return transaction


@router.delete("/{transaction_id}", summary="Delete the Transaction by id.")
async def delete_transaction(transaction_id: int):
    transaction = fake_transactions_db.get(transaction_id)

    errors.handle_not_found_error(
        entity_id=transaction_id,
        entity_name="Transaction",
        entity=transaction,
    )

    del fake_transactions_db[transaction_id]
    return {}







