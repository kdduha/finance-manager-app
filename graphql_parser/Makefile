.PHONY: graphql-run-local
graphql-run-local: # Run the graphql app locally.
	python3 -m graphql_parser.main

 .PHONY: graphql-build-docker
graphql-build-docker: # Build graphql Dockerfile.
	docker build -t graphql-api -f graphql_parser/Dockerfile .

.PHONY: graphql-run-docker
graphql-run-docker: # Run the parser app in the docker container.
	docker run -d -p 8090:8090 graphql-api
