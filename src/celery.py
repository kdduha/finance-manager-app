import requests

import src.errors as errors
from celery import Celery
from src.config import cfg

celery_app = Celery("worker", broker=cfg.parser.celery_broker_url, backend=cfg.parser.celery_backend_url)


@celery_app.task
def parse_url_task(count: int) -> dict:
    try:
        response = requests.get(f"{cfg.parser.parser_url}/parse", params={"count": count}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        raise errors.BadRequestException(detail=f"Request error: {str(e)}")
    except ValueError:
        raise errors.BadRequestException(detail="Invalid JSON response from parser service")
