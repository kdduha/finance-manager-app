from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.schemas.budgets import *
from src.schemas.users import User
from src.schemas.categories import Category
from src.schemas.base import DELETE_MODEL_RESPONSE
import src.utils.errors as errors
import src.db as db

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
    responses=errors.error_responses(
        errors.NotFoundException, errors.ValidationException,
    ),
)


@router.post("/", summary="Create a new Budget.", response_model=Budget)
def create_budget(request: BudgetDefault, session: Session = Depends(db.get_session)):
    request.custom_validate(start_date=request.start_date, end_date=request.end_date)

    user = session.get(User, request.user_id)
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    category = session.get(Category, request.category_id)
    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=request.category_id)

    budget = Budget(**request.dict(), created_at=datetime.utcnow())

    session.add(budget)
    session.commit()
    session.refresh(budget)

    return budget


@router.get("/", summary="Get a list of all budgets.", response_model=list[Budget])
async def list_budgets(
        user_id: int | None = Query(None, description="Filter by User ID"),
        category_id: int | None = Query(None, description="Filter by Category ID"),
        session: Session = Depends(db.get_session)
):
    query = session.query(Budget)

    if user_id:
        query = query.filter(Budget.user_id == user_id)
    if category_id:
        query = query.filter(Budget.category_id == category_id)

    budgets = query.all()
    return budgets


@router.get("/{budget_id}", summary="Get the Budget by id.", response_model=Budget)
async def get_budget(budget_id: int, session: Session = Depends(db.get_session)):
    budget = session.query(Budget).filter(Budget.id == budget_id).first()

    if budget is None:
        raise errors.NotFoundException(entity_name="Budget", entity_id=budget_id)

    return budget


@router.put("/{budget_id}", summary="Update the Budget by id.", response_model=Budget)
async def update_budget(budget_id: int, request: BudgetUpdate, session: Session = Depends(db.get_session)):
    budget = session.query(Budget).filter(Budget.id == budget_id).first()

    if budget is None:
        raise errors.NotFoundException(entity_name="Budget", entity_id=budget_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(budget, key, value)

    session.commit()
    session.refresh(budget)

    return budget


@router.delete("/{budget_id}", summary="Delete the Budget by id.", responses={200: DELETE_MODEL_RESPONSE})
async def delete_budget(budget_id: int, session: Session = Depends(db.get_session)) :
    budget = session.query(Budget).filter(Budget.id == budget_id).first()

    if budget is None:
        raise errors.NotFoundException(entity_name="Budget", entity_id=budget_id)

    session.delete(budget)
    session.commit()
