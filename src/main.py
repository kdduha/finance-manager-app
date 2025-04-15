from src import db, app
import uvicorn

app = app.init()


@app.on_event("startup")
def on_startup():
    db.init()


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
