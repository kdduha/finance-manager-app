from src import db, app
from src.config import cfg
import uvicorn

app = app.init()


@app.on_event("startup")
def on_startup():
    db.init()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=cfg.uvicorn.host,
        port=cfg.uvicorn.port,
        workers=cfg.uvicorn.workers,
        log_level=cfg.uvicorn.log_level,
    )
