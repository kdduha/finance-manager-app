from fastapi import FastAPI

from src.routers import users, categories, transactions, budgets, tags, goals
import src.utils.errors as errors

routers = [
    users.router,
    categories.router,
    tags.router,
    transactions.router,
    budgets.router,
    goals.router,
]

exceptions = {
    errors.NotFoundException: errors.not_found_exception_handler,
    errors.ValidationException: errors.validation_exception_handler
}


def init() -> FastAPI:
    new_app = FastAPI()

    for router in routers:
        new_app.include_router(router)

    for exc, handler in exceptions.items():
        new_app.add_exception_handler(exc, handler)

    return new_app

