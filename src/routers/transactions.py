from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

import src.db as db
import src.errors as errors
from src.auth import auth
from src.schemas.base import DELETE_MODEL_RESPONSE
from src.schemas.categories import Category, TransactionWithCategory
from src.schemas.tags import Tag, TransactionTagLink, TransactionWithTags
from src.schemas.transactions import Transaction, TransactionCreate, TransactionUpdate
from src.schemas.users import User

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    responses=errors.error_responses(
        errors.NotFoundException,
        errors.ValidationException,
        errors.AuthorizationException,
    ),
)


@router.post("/", summary="Create a new Transaction.", response_model=TransactionWithTags)
async def create_transaction(
    request: TransactionCreate,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    user = session.get(User, request.user_id)
    if not user:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    category = session.get(Category, request.category_id)
    if not category:
        raise errors.NotFoundException(entity_name="Category", entity_id=request.category_id)

    transaction = Transaction(
        user_id=request.user_id,
        category_id=request.category_id,
        amount=request.amount,
        date=request.date,
        description=request.description,
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    if request.tag_ids:
        for tag_id in request.tag_ids:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                transaction_tag_link = TransactionTagLink(transaction_id=transaction.id, tag_id=tag.id)
                session.add(transaction_tag_link)

        session.commit()

    return TransactionWithTags(
        id=transaction.id,
        user_id=transaction.user_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        date=transaction.date,
        description=transaction.description,
        tags=transaction.tags,
    )


@router.get("/", summary="List Transactions.", response_model=list[Transaction])
async def list_transactions(
    user_id: int | None = Query(None),
    category_id: int | None = Query(None),
    description: str | None = Query(None),
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    query = session.query(Transaction)

    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if description:
        query = query.filter(Transaction.description.ilike(f"%{description}%"))

    return query.all()


@router.get("/{transaction_id}", summary="Get Transaction by ID", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise errors.NotFoundException(entity_name="Transaction", entity_id=transaction_id)

    return transaction


@router.put("/{transaction_id}", summary="Update Transaction", response_model=Transaction)
async def update_transaction(
    transaction_id: int,
    request: TransactionUpdate,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise errors.NotFoundException(entity_name="Transaction", entity_id=transaction_id)

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)

    session.commit()
    session.refresh(transaction)
    return transaction


@router.delete(
    "/{transaction_id}",
    summary="Delete Transaction",
    responses={status.HTTP_200_OK: DELETE_MODEL_RESPONSE},
)
async def delete_transaction(
    transaction_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise errors.NotFoundException(entity_name="Transaction", entity_id=transaction_id)

    session.delete(transaction)
    session.commit()

    return {"detail": f"Transaction with id {transaction_id} has been deleted."}


@router.get(
    "/{transaction_id}/with-category",
    summary="Get a specific transaction with Category details.",
    response_model=TransactionWithCategory,
)
async def get_transaction_with_category(
    transaction_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise errors.NotFoundException(entity_name="Transaction", entity_id=transaction_id)

    return TransactionWithCategory(
        id=transaction.id,
        user_id=transaction.user_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        date=transaction.date,
        description=transaction.description,
        category=transaction.category,
    )


@router.get(
    "/{transaction_id}/with-tags",
    summary="Get a specific transaction with Tags details.",
    response_model=TransactionWithTags,
)
async def get_transaction_with_tags(
    transaction_id: int,
    session: Session = Depends(db.get_session),
    _: User = Depends(auth.get_current_user),
):
    transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise errors.NotFoundException(entity_name="Transaction", entity_id=transaction_id)

    return TransactionWithTags(
        id=transaction.id,
        user_id=transaction.user_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        date=transaction.date,
        description=transaction.description,
        tags=transaction.tags,
    )
