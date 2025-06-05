import time
from fastapi import FastAPI, Query

from parser.fetch import gather_details, fetch_vc_money_posts_selenium

app = FastAPI()


@app.get("/parse", response_model=dict)
async def parse_vc_posts(count: int = Query(10, ge=1, le=500)):
    posts = fetch_vc_money_posts_selenium(desired_count=count)
    start = time.monotonic()
    detailed_posts = await gather_details(posts)
    elapsed = round(time.monotonic() - start, 2)

    return {
        "meta": {"parsed": len(detailed_posts), "duration_seconds": elapsed},
        "posts": [post.dict() for post in detailed_posts]
    }


