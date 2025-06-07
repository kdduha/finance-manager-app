include parser/Makefile
include graphql_parser/Makefile

default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile \
		| while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: freeze
freeze: # Freeze all requirements.
	pip freeze > requirements.txt

.PHONY: install-local
install-local: # Install all requirements locally.
	pip install -r requirements.txt

.PHONY: run-local
run-local: # Run the app locally.
	 python3 -m src.main

 .PHONY: build-docker
build-docker: # Build finance-manager-app Dockerfile.
	docker build -t finance-manager-app .

.PHONY: build-k8s
build-k8s: # Deploy the app in k8s.
	eval $$(minikube docker-env) && make build-docker && sh deploy/k8s/deploy_app.sh

.PHONY: monitor-k8s
monitor-k8s: # Deploy grafana and prometheus in k8s
	sh deploy/k8s/deploy_monitoring.sh

.PHONY: run-docker
run-docker: # Run the app in the docker container.
	docker run --name finance-manager-app-container -d \
	  -p 8000:8000 \
	  --env-file .env \
	  -e UVICORN_HOST=0.0.0.0 \
	  -e DB_HOST=host.docker.internal \
	  finance-manager-app

.PHONY: compose-docker
compose-docker: # Up the app with Prometheus and Grafana as a docker-compose.
	docker-compose -f deploy/docker/docker-compose.yaml up --build

.PHONY: init-migration
init-migration: # Create alembic migration.
	alembic init migrations

.PHONY: create-migration
create-migration: # Create alembic migration files. Use MESSAGE var to set revision message.
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ MESSAGE is required. Usage: make create-migration MESSAGE='your message here'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: do-migration
do-migration: # Apply latest migrations.
	alembic upgrade head

.PHONY: migrate
migrate: # Create and apply migration in one step.
	@$(MAKE) create-migration MESSAGE="$(MESSAGE)"
	@$(MAKE) do-migration

.PHONY: lint
lint: # Lint the whole project with black, isort and flake8 (install, if not installed).
	bash .build/check_and_lint.sh

.PHONY: openapi
openapi: # Download the OpenAPI protocol from the running app.
	curl -sL http://localhost:8000/openapi.json \
 	| jq . > media/openapi.json