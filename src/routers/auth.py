from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import src.db as db
import src.errors as errors
from src.auth import auth
from src.schemas.users import Token, User, UserDefault, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses=errors.error_responses(
        errors.NotFoundException,
        errors.ValidationException,
        errors.AuthorizationException,
        errors.BadRequestException,
    ),
)


@router.post("/register", response_model=User, summary="Register a new user")
def register(req: UserDefault, session: Session = Depends(db.get_session)):

    req.custom_validate(birth_date=req.birth_date)

    existing_user = db.find_user(req.email)
    if existing_user:
        raise errors.BadRequestException(detail="User with this email already exists")

    hashed_password = auth.get_password_hash(req.password)
    user = User(
        **req.dict(exclude={"password"}),
        password=hashed_password,
        created_at=datetime.utcnow(),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post("/login", response_model=Token, summary="Login user and return JWT token")
def login(credentials: UserLogin, session: Session = Depends(db.get_session)):

    user = session.query(User).filter(User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.password):
        raise errors.AuthorizationException(detail="Invalid email or password")

    token = auth.encode_token(user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=User, summary="Get current user info")
def get_me(current_user: User = Depends(auth.get_current_user)):
    return current_user
