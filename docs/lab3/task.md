# Описание выполненной работы

В этой работе мы расширили существующее FastAPI-приложение, упаковали его и сопутствующие компоненты (Parser, PostgreSQL, Redis/Celery, Grafana/Prometheus) в Docker-окружение, а также реализовали асинхронный вызов Parser-сервиса через очередь задач. В отчёте приведены ключевые моменты реализации, использованные технологии и фрагменты кода, демонстрирующие основные идеи.

### Конфигурация через Pydantic Settings

Основная конфигурация приложения (`src/config.py`) оформлена через `pydantic_settings.BaseSettings`. Для каждого компонента (Uvicorn, база данных, Auth, Parser, Prometheus) создан свой класс-настройка, читающий переменные из `.env`. Класс `ParserConfig` получил префикс `PARSER_` и параметры:

```python
class ParserConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PARSER_")

    enabled: bool
    parser_url: str
    celery_broker_url: str
    celery_backend_url: str
```

При загрузке `cfg = Config.load()` все эти поля подтягиваются автоматически. В `main` и в роутерах проверяется `cfg.parser.enabled`, чтобы прекратить работу Parser-функционала, если он выключен.

---

### Parser-сервис и Dockerfile

Parser реализован как отдельное FastAPI-приложение в каталоге `parser/`. В файле `parser/main.py` определён роутер, который принимает GET-запрос `/parse?count=<n>`, обрабатывает его (сбор ссылок или любой другой логикой) и возвращает JSON со структурой:

```json
{
  "meta": { "parsed": 10, "duration_seconds": 0.23 },
  "posts": [
    { "title": "Post1", "link": "https://...", "text": "...", "error": null },
    ...
  ]
}
```

Dockerfile для Parser-контейнера (`parser/Dockerfile`) основан на `python:3.11-slim`, устанавливает зависимости (включая `chromium-driver` и всё необходимое для самого парсера) и запускает `uvicorn parser.main:app --host 0.0.0.0 --port 8080`.

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl unzip gnupg chromium-driver \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY parser/requirements.txt ./parser/requirements.txt
RUN pip install --no-cache-dir -r parser/requirements.txt
COPY parser/ ./parser/
EXPOSE 8080
CMD ["uvicorn", "parser.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

### Celery + Redis: асинхронная очередь

Для асинхронной обработки парсинга был добавлен Celery-таргет вместе с Redis-брокером. Файл `src/celery.py` содержит инициализацию Celery и определение задачи `parse_url_task`:

```python
from celery import Celery
import requests
import src.errors as errors
from src.config import cfg

celery_app = Celery(
    "worker",
    broker=cfg.parser.celery_broker_url,
    backend=cfg.parser.celery_backend_url
)

@celery_app.task(bind=True)
def parse_url_task(self, count: int) -> dict:
    try:
        url = f"{cfg.parser.parser_url}/parse"
        response = requests.get(url, params={"count": count}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise errors.BadRequestException(detail=f"Request error: {e}")
    except ValueError:
        raise errors.BadRequestException(detail="Invalid JSON from parser")
```

* `bind=True` даёт доступ к `self.request.id` и `self.retry()`.
* Внутри задачи делается HTTP-запрос к отдельному Parser-сервису, возвращается JSON либо бросается кастомная ошибка.

---

### FastAPI-роутер для Parser

В `src/routers/parser.py` организованы два эндпоинта, защищённые JWT-авторизацией (через `Depends(auth.get_current_user)`), и обвязка ошибок по примеру других роутеров:

```python
from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from pydantic import BaseModel
from typing import Optional

import src.errors as errors
from src.auth import auth
from src.celery import celery_app, parse_url_task
from src.config import cfg
from src.schemas.parser import ParseResult

router = APIRouter(
    prefix="/parser",
    tags=["Parser"],
    responses=errors.error_responses(
        errors.BadRequestException,
        errors.AuthorizationException
    ),
)

class ParseRequest(BaseModel):
    count: int

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[ParseResult] = None

@router.post("/parse")
def start_parsing(req: ParseRequest, _=Depends(auth.get_current_user)):
    if not cfg.parser.enabled:
        raise errors.BadRequestException(detail="Parser is disabled")
    task = parse_url_task.delay(req.count)
    return {"task_id": task.id, "message": "Parsing started"}

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str, _=Depends(auth.get_current_user)):
    if not cfg.parser.enabled:
        raise errors.BadRequestException(detail="Parser is disabled")

    result = AsyncResult(task_id, app=celery_app)
    if result.failed():
        exc = result.result
        if isinstance(exc, errors.BadRequestException):
            raise errors.BadRequestException(detail=exc.detail)
        raise errors.BadRequestException(detail="Unknown error in parsing task")

    payload = None
    if result.successful():
        payload = ParseResult.parse_obj(result.result)
    return TaskStatusResponse(task_id=task_id, status=result.status, result=payload)
```

* `ParseResult` описан в `src/schemas/parser.py` как Pydantic-модель с полями `meta` и списком `posts`.
* При успешном завершении фоновой задачи возвращается готовый JSON из Parser-сервиса.

---

### Docker Compose: оркестрация сервисов

Финальный `docker-compose.yml` (файл `deploy/docker/docker-compose.yaml`) объединяет шесть сервисов:

* **web**: основной FastAPI (служит API, использует Postgres, Celery)
* **parser**: отдельное FastAPI-приложение для парсинга (порт 8080)
* **postgres**: база данных PostgreSQL (порт 5432)
* **redis**: брокер сообщений для Celery (порт 6379)
* **celery\_worker**: контейнер с Celery-воркером, который слушает очередь
* **prometheus**, **grafana**: мониторинг (порт 9090 и 3000)

Ключевые фрагменты `docker-compose.yml` (сокращённый вид):

```yaml
services:
  web:
    build: ../../
    ports:
      - "8000:8000"
    env_file:
      - ../../.env
    environment:
      UVICORN_HOST: "0.0.0.0"
      DB_HOST: "postgres"
      DB_PASSWORD: "12345"
      PARSER_ENABLED: "true"
      PARSER_PARSER_URL: "http://parser:8080"
      PARSER_CELERY_BROKER_URL: "redis://redis:6379/0"
      PARSER_CELERY_BACKEND_URL: "redis://redis:6379/0"
    depends_on:
      - postgres
      - redis
      - parser

  parser:
    build:
      context: ../../
      dockerfile: ./parser/Dockerfile
    ports:
      - "8080:8080"
    environment:
      ENV: "DOCKER"
    depends_on:
      - prometheus

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: "kdduha"
      POSTGRES_PASSWORD: "12345"
      POSTGRES_DB: "fastapi_db"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: ../../
    working_dir: /usr/app/src
    command: celery -A celery:celery_app worker --loglevel=info
    env_file:
      - ../../.env
    environment:
      PARSER_ENABLED: "true"
      PARSER_PARSER_URL: "http://parser:8080"
      PARSER_CELERY_BROKER_URL: "redis://redis:6379/0"
      PARSER_CELERY_BACKEND_URL: "redis://redis:6379/0"
    depends_on:
      - redis
      - parser

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ../../deploy/docker/prometheus.yaml:/etc/prometheus/prometheus.yaml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  grafana_data:
```
