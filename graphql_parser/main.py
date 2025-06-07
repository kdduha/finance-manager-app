import uvicorn
import strawberry
from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter

from graphql_parser.schema import Query
from graphql_parser.db import get_session
from graphql_parser.config import cfg


def create_app() -> FastAPI:
    app = FastAPI()

    schema = strawberry.Schema(query=Query)
    graphql_app = GraphQLRouter(
        schema,
        context_getter=lambda db=Depends(get_session): {"db": db}
    )

    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
         "graphql_parser.main:app",
        host=cfg.uvicorn.host,
        port=cfg.uvicorn.port,
        workers=cfg.uvicorn.workers,
        log_level=cfg.uvicorn.log_level,
        reload=cfg.uvicorn.reload,
    )
