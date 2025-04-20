from fastapi import FastAPI

import src.errors as errors
from src.routers import auth, budgets, categories, goals, tags, transactions, users

# === Base Routers ===

routers = [
    auth.router,
    users.router,
    categories.router,
    tags.router,
    transactions.router,
    budgets.router,
    goals.router,
]

# === Errors To Handlers Map ===

exceptions = {
    errors.NotFoundException: errors.not_found_exception_handler,
    errors.ValidationException: errors.validation_exception_handler,
    errors.AuthorizationException: errors.authorization_exception_handler,
    errors.BadRequestException: errors.bad_request_exception_handler,
}


def init() -> FastAPI:
    new_app = FastAPI()

    for router in routers:
        new_app.include_router(router)

    for exc, handler in exceptions.items():
        new_app.add_exception_handler(exc, handler)

    return new_app
