from pydantic import BaseModel


class Post(BaseModel):
    title: str
    link: str


class DetailedPost(BaseModel):
    title: str = None
    link: str
    text: str = None
    error: str = None
