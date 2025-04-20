import uvicorn

from src import app, db
from src.config import cfg

app = app.init()

if __name__ == "__main__":
    db.init()
    uvicorn.run(
        "src.main:app",
        host=cfg.uvicorn.host,
        port=cfg.uvicorn.port,
        workers=cfg.uvicorn.workers,
        log_level=cfg.uvicorn.log_level,
        reload=True,
    )
