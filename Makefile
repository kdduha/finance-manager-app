default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile \
		| while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: install-local
install-local: # Install all requirements locally.
	pip install -r requirements.txt

.PHONY: run-local
run-local: # Run the app locally.
	 python3 -m src.main

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