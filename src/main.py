import uvicorn
from src.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app",  reload=True)
