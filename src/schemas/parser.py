from pydantic import BaseModel


class Post(BaseModel):
    title: str | None
    link: str


class DetailedPost(BaseModel):
    title: str | None = None
    link: str
    text: str | None = None
    error: str | None = None


class Meta(BaseModel):
    parsed: int
    duration_seconds: float


class ParseResult(BaseModel):
    meta: Meta
    posts: list[DetailedPost]


class ParseRequest(BaseModel):
    count: int


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: ParseResult | None = None
