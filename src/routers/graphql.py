import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from src.config import cfg

router = APIRouter(
    prefix="",
    tags=["GraphQL"],
)

GRAPHQL_SERVICE_BASE = cfg.graphql.url
GRAPHQL_ENDPOINT = f"{GRAPHQL_SERVICE_BASE}/graphql"


@router.api_route("/graphql", methods=["GET", "POST"])
async def graphql_proxy(request: Request):
    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient() as client:
        try:
            proxied = await client.request(
                method=request.method,
                url=GRAPHQL_ENDPOINT,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=body,
                params=params,
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error connecting to GraphQL service: {exc}")

    return Response(
        content=proxied.content,
        status_code=proxied.status_code,
        headers=dict(proxied.headers),
        media_type=proxied.headers.get("content-type"),
    )
