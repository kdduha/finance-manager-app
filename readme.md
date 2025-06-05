# Finance Manager API App

<div id="stack-badges">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python%20Version-3.11-blue?style=flat-square" alt="Python 3.11"/>
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  </a>
  <a href="https://alembic.sqlalchemy.org/en/latest/">
    <img src="https://img.shields.io/badge/Alembic-23374D?style=flat-square&logo=alembic&logoColor=white" alt="Alembic"/>
  </a>
  <a href="https://www.sqlalchemy.org/">
    <img src="https://img.shields.io/badge/SQLAlchemy-CA504E?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  </a>
  <a href="https://kubernetes.io/">
    <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white" alt="Kubernetes"/>
  </a>
  <a href="https://docs.celeryproject.org/">
    <img src="https://img.shields.io/badge/Celery-ff6600?style=flat-square&logo=celery&logoColor=white" alt="Celery"/>
  </a>
  <a href="https://redis.io/">
    <img src="https://img.shields.io/badge/Redis-D82C20?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  </a>
  <a href="https://grafana.com/">
    <img src="https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white" alt="Grafana"/>
  </a>
  <a href="https://prometheus.io/">
    <img src="https://img.shields.io/badge/Prometheus-FF6C37?style=flat-square&logo=prometheus&logoColor=white" alt="Prometheus"/>
  </a>
</div>


---

The goal of this project is to practice writing a FastAPI backend in Python, with the following features:

* The API uses PostgreSQL as the database
* Migrations are handled using Alembic
* Authentication is implemented using JWT
* Celery + Redis for background tasks (parser)
* A linter is set up along with a GitHub workflow for linting
* The application configuration is managed via environment variables

OpenAPI (Swagger) documentation can be found at `media/openapi.json`.

In order to check all available utils `Makefile` commands type: 
```shell
make
```

And see the available commands below. 
Some cmds require additional packages in order to run:
```yaml
# cmds example
help: Show help for each of the Makefile recipes.
install-local: Install all requirements locally.
freeze: Freeze all requirements.
run-local: Run the app locally.
init-migration: Create alembic migration.
create-migration: Create alembic migration files. Use MESSAGE var to set revision message.
do-migration: Apply latest migrations.
migrate: Create and apply migration in one step.
lint: Lint the whole project with black, isort and flake8 (install, if not installed).
openapi: Download the OpenAPI protocol from the running app.
```

## How to run the app?

There are three main ways:

### 1. Manual (local Python)

1. Create and activate a new Python virtual environment.
2. Install requirements:

   ```sh
   pip install -r requirements.txt
   ```
3. Copy or rename `.env.example` → `.env`, and fill in all required variables (Postgres, JWT, parser, etc.).
4. Run the application:

   ```sh
   make run-local
   ```

   This runs `python3 -m src.main`, which starts Uvicorn on `localhost:8000` by default.

---

### 2. Docker Compose

1. Ensure Docker (and Docker Compose) is installed
2. Copy or rename `.env.example` → `.env`, fill in all variables
3. From the repo root, run:

   ```sh
   make compose-docker
   ```

   This will build and start:

   * **web** (FastAPI + PostgreSQL connection) on port `8000`
   * **parser** (your separate parser image) on port `8080`
   * **redis** (Redis broker for Celery) on port `6379`
   * **celery\_worker** (Celery worker consuming tasks)
   * **postgres** (PostgreSQL) on port `5432`
   * **prometheus** on port `9090`
   * **grafana** on port `3000`

   The FastAPI app will be reachable at `http://localhost:8000`, and Celery tasks will be processed in the background using Redis.

---

### 3. Kubernetes (minikube)

> **Prerequisites**: `minikube`, `kubectl`, Docker.

1. Start Minikube (if not already running):

   ```sh
   minikube start
   ```
2. From the repo root, build the Docker image inside minikube’s Docker daemon and deploy:

   ```sh
   make build-k8s
   ```

   This does:

   * `eval $(minikube docker-env)` to point Docker CLI at minikube’s Docker
   * `docker build -t finance-manager-app .`
   * `sh deploy/k8s/deploy_app.sh` which applies Kubernetes manifests for the main api app
3. To verify, open your browser to `http://localhost:8000`.
4. (Optional) Deploy Prometheus + Grafana to Kubernetes:

   ```sh
   make monitor-k8s
   ```

---

## DataBase API Model

![dataplane](./media/database.png)

## Notes

* **Celery Worker** runs in a separate container (`celery-worker`) and listens to Redis. It periodically polls the queue. Without it, no background tasks would be executed.
* **Parser Service** is a separate container exposing `/parse?count=<n>`. The Celery task does `GET http://parser:8080/parse?count=<n>`, processes the JSON, and returns it to be stored in Redis backend.
* **FastAPI** enqueues tasks via `parse_url_task.delay(count)` and provides an endpoint to check `AsyncResult(task_id)`.

