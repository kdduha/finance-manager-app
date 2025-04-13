from fastapi import FastAPI, APIRouter

from src.routers import users, categories, transactions, budgets

routers = [
    users.router,
    categories.router,
    transactions.router,
    budgets.router
]


def create_app() -> FastAPI:
    new_app = FastAPI()

    for router in routers:
        new_app.include_router(router)

    return new_app
