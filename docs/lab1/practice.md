Вся практика была сделана на основе моего варианта, что в последующем легко в базу всей лаборатной работы. 

## Задание 1

Необходимо было сделать базовую структуру проекта на FastAPI с использованием mock-ов базы данных 
на словарях. Работа реализована [1-ым коммитом](https://github.com/kdduha/finance-manager-app/pull/1/commits/4c96e85a73e9e15ad8b221598ee6d8884a661fed).

- добавлены базовые зависимости проекта
- спроектирована модель данных для будущей БД (ниже представлена уже финальная модель данных всего проекта, которая дорабатывалась в процесск)
![dataplane](../../media/database.png)
- сделан базовый шаблон для будущих вспомогательных Makefile команд
```makefile
default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
    @grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile \
        | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: install-local
install-local: # Install all requirements locally.
    pip install -r requirements.txt

.PHONY: run-local
run-local: # Run the app locally.
     python3 -m src.main
```
- все эндпоинты разделены на отдельные роутеры и реализованы через mock-базы данных в виде словарей.
Так как во многом код похожий для разных сервисов, приведу только листинг кода для сущности "Категории":
```python
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
```
По факту мы просто сериализируем и десериализируем модели данных в словари, добавив базовый код для работы с эндпоинтами,
который будет в будущем расширяться.

## Задание 2

Во втором задании необходимо было подключить базу данных. Коммит выполненной практик находится [здесь](https://github.com/kdduha/finance-manager-app/pull/1/commits/9111392b1d4f71e7ea9536335bba6f3fadfd3c4c).
Из основных изменений можно перечислить следующие:

- добавлено подключение к БД
- добавлено использование ORM как FastAPI dependency. Пример на все той же группе эндпоинтов для "Категория":
```python
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from src.schemas.categories import *
from src.schemas.users import User
from src.schemas.base import DELETE_MODEL_RESPONSE
import src.utils.errors as errors
import src.db as db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses=errors.error_responses(
        errors.NotFoundException, errors.ValidationException,
    ),
)


@router.post("/", summary="Create a new Category.", response_model=Category)
async def create_category(request: CategoryDefault, session: Session = Depends(db.get_session)):
    request.custom_validate(type=request.type)

    user = session.get(User, request.user_id)
    if user is None:
        raise errors.NotFoundException(entity_name="User", entity_id=request.user_id)

    category = Category(**request.dict())

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


@router.get("/{category_id}", summary="Get the Category by id.", response_model=Category)
async def get_category(category_id: int, session: Session = Depends(db.get_session)):
    category = session.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    return category


@router.get("/", summary="List the Category.", response_model=list[Category])
async def list_category(
        user_id: str | None = Query(None, description="Filter by User ID"),
        name: str | None = Query(None, description="Filter by Category Name"),
        cat_type: CategoryType | None = Query(None, description="Filter by Category Type"),
        session: Session = Depends(db.get_session)
):
    query = session.query(Category)

    if user_id:
        query = query.filter(Category.user_id == user_id)
    if name:
        query = query.filter(Category.name.ilike(f"%{name}%"))
    if cat_type:
        query = query.filter(Category.type == cat_type)

    categories = query.all()
    return categories


@router.put("/{category_id}", summary="Update the Category by id.", response_model=Category)
async def update_category(category_id: int, request: CategoryUpdate, session: Session = Depends(db.get_session)):
    category = session.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(category, key, value)

    session.commit()
    session.refresh(category)

    return category


@router.delete("/{category_id}", summary="Delete the Category by id.", responses={200: DELETE_MODEL_RESPONSE})
async def delete_user(category_id: int, session: Session = Depends(db.get_session)):
    category = session.query(Category).filter(Category.id == category_id).first()

    if category is None:
        raise errors.NotFoundException(entity_name="Category", entity_id=category_id)

    session.delete(category)
    session.commit()

    return {"detail": f"Category with id {category_id} has been deleted."}
```
- переработанные модели данных в коде для "Категорий"
```python
from enum import Enum
from sqlmodel import Field, Relationship
from datetime import datetime
from decimal import Decimal

from src.schemas.base import BaseSQLModel


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class CategoryDefault(BaseSQLModel):
    name: str
    type: CategoryType
    user_id: int = Field(foreign_key="user.id")


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: "User" = Relationship(back_populates="categories")
    transactions: list["Transaction"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class CategoryUpdate(BaseSQLModel):
    name: str | None


class TransactionWithCategory(BaseSQLModel):
    id: int
    user_id: int
    category_id: int
    amount: Decimal
    date: datetime
    description: str | None = None
    category: Category
```
- при этом была создана базовая модель, которая умеет в кастомные валидации необходимых параметров (например, проверка даты на будущее/прошлое).
Таким образом, наследуясь от одного класса, можно было переиспользовать его валидацию в дочерних
```python
from sqlmodel import SQLModel
from enum import Enum
from datetime import datetime
from src.utils import errors
from typing import Any, Type

DELETE_MODEL_RESPONSE = {
    "description": "User successfully deleted",
    "content": {
        "application/json": {
            "example": {"message": "string"}
        }
    }
}


class BaseSQLModel(SQLModel):

    @staticmethod
    def validate_past_data(date: Any, field_name: str) -> None:
        if isinstance(date, datetime):
            # delete info about Time Zone
            date = date.replace(tzinfo=None)
            current_time = datetime.utcnow().replace(tzinfo=None)

            if date > current_time:
                error = errors.ValidationException(
                    errors.ValidationExceptionDetail(
                        loc=["body", field_name],
                        msg="Date should be in the past",
                        type=f"{type(date)}"
                    )
                )
                raise error

    @staticmethod
    def validate_future_date(date: Any, field_name: str) -> None:
        if isinstance(date, datetime):
            # delete info about Time Zone
            date = date.replace(tzinfo=None)
            current_time = datetime.utcnow().replace(tzinfo=None)

            if current_time >= date:
                error = errors.ValidationException(
                    errors.ValidationExceptionDetail(
                        loc=["body", field_name],
                        msg="Date should be in the future",
                        type=f"{type(date)}"
                    )
                )
                raise error
```
- возника также необходимость с корректным отображением ошибок в swagger, для чего все ошибки были обернуты в отдельные exceptions и хендлеры
```python
from fastapi import Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Any, ClassVar, List, Union, Type


# === Custom Errors ===

class NotFoundException(Exception):
    status: ClassVar[int] = 404
    detail: str

    def __init__(self, entity_name: str, entity_id: int):
        self.detail = f"{entity_name} <{entity_id}> not found."

    def json(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": self.detail}
        )

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Entity not found",
                "content": {
                    "application/json": {
                        "example": {"detail": "string"}
                    }
                }
            }
        }


class ValidationExceptionDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class ValidationException(Exception):
    status: ClassVar[int] = 422
    detail: ValidationExceptionDetail

    def __init__(self, errors: ValidationExceptionDetail):
        self.detail = errors

    def json(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": self.detail.dict()}
        )

    @classmethod
    def response(cls) -> dict[int, dict[str, Any]]:
        return {
            cls.status: {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "loc": ["body", "string"],
                                "msg": "string",
                                "type": "Type[]"
                            }
                        }
                    }
                }
            }
        }


# === Errors Handlers ===

async def validation_exception_handler(_: Request, exc: ValidationException):
    return exc.json()


async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return exc.json()


# === Utils ===

def error_responses(*errors: Type[Exception]) -> dict[int, dict[str, Any]]:
    responses = {}
    for error in errors:
        responses.update(error.response())
    return responses
```

## Задание 3

В третьем задании (вот [коммит](https://github.com/kdduha/finance-manager-app/pull/1/commits/331260187cf562ec88b0b562e7b9bfc880c180d9)) в основном
были структурные улучшения проекта и добавление миграций:
- добавлен многосоставной конфиг, который парсится полностью из env
```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class UvicornConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="UVICORN_")

    host: str = Field("127.0.0.1")
    port: int = Field(8000)
    workers: int | None = Field(None)
    log_level: str = Field("info")


class DataBaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str
    port: int = 5432
    user: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Config(ConfigBase):
    uvicorn: UvicornConfig = Field(default_factory=UvicornConfig)
    db: DataBaseConfig = Field(default_factory=DataBaseConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


cfg = Config.load()
```

Теперь запуск приложения выглядит в коде буквально так:
```python
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=cfg.uvicorn.host,
        port=cfg.uvicorn.port,
        workers=cfg.uvicorn.workers,
        log_level=cfg.uvicorn.log_level,
    )
```
- обновлен и сформирован .gitignore
- добавлен и сгенерированы миграции, а также скрипты по их запуску
```makefile
.PHONY: init-migration
init-migration: # Create alembic migration.
	alembic init migrations

.PHONY: create-migration
create-migration: # Create alembic migration files. Use MESSAGE var to set revision message.
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ MESSAGE is required. Usage: make create-migration MESSAGE='your message here'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: do-migration
do-migration: # Apply latest migrations.
	alembic upgrade head

.PHONY: migrate
migrate: # Create and apply migration in one step.
	@$(MAKE) create-migration MESSAGE="$(MESSAGE)"
	@$(MAKE) do-migration
```