from fastapi import APIRouter, Query, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from src.schemas.goals import Goal, GoalDefault, GoalUpdate
from src.schemas.users import User
from src.schemas.base import DELETE_MODEL_RESPONSE
import src.utils.errors as errors
import src.db as db

router = APIRouter(
    prefix="/goals",
    tags=["Goals"],
    responses=errors.error_responses(
        errors.NotFoundException, errors.ValidationException,
    ),
)


@router.post("/", summary="Create a new Goal.", response_model=Goal)
async def create_goal(request: GoalDefault, session: Session = Depends(db.get_session)):
    request.custom_validate(deadline=request.deadline)

    user = session.get(User, request.user_id)
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    goal = Goal(**request.dict(), created_at=datetime.utcnow())

    session.add(goal)
    session.commit()
    session.refresh(goal)

    return goal


@router.get("/{goal_id}", summary="Get the Goal by id.", response_model=Goal)
async def get_goal(goal_id: int, session: Session = Depends(db.get_session)):
    goal = session.query(Goal).filter(Goal.id == goal_id).first()

    if goal is None:
        raise errors.NotFoundException(entity_name="Goal", entity_id=goal_id)

    return goal


@router.get("/", summary="List all Goals.", response_model=list[Goal])
async def list_goals(
        user_id: int | None = Query(None, description="Filter by User ID"),
        name: str | None = Query(None, description="Filter by Goal Name"),
        session: Session = Depends(db.get_session)
):
    query = session.query(Goal)

    if user_id:
        query = query.filter(Goal.user_id == user_id)
    if name:
        query = query.filter(Goal.name.ilike(f"%{name}%"))

    goals = query.all()
    return goals


@router.put("/{goal_id}", summary="Update the Goal by id.", response_model=Goal)
async def update_goal(goal_id: int, request: GoalUpdate, session: Session = Depends(db.get_session)):
    goal = session.query(Goal).filter(Goal.id == goal_id).first()
    if goal is None:
        raise errors.NotFoundException(entity_name="Goal", entity_id=goal_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(goal, key, value)

    session.commit()
    session.refresh(goal)

    return goal


@router.delete("/{goal_id}", summary="Delete the Goal by id.", responses={200: DELETE_MODEL_RESPONSE})
async def delete_goal(goal_id: int, session: Session = Depends(db.get_session)):
    goal = session.query(Goal).filter(Goal.id == goal_id).first()

    if goal is None:
        raise errors.NotFoundException(entity_name="Goal", entity_id=goal_id)

    session.delete(goal)
    session.commit()

    return {"detail": f"Goal with id {goal_id} has been deleted."}
