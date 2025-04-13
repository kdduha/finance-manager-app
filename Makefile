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