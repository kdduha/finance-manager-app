.PHONY: parser-run-local
parser-run-local: # Run the parser app locally.
	uvicorn parser.main:app --host 0.0.0.0 --port 8080

 .PHONY: parser-build-docker
parser-build-docker: # Build parser Dockerfile.
	docker build -t parser-api -f parser/Dockerfile .

.PHONY: parser-run-docker
parser-run-docker: # Run the parser app in the docker container.
	docker run -d -p 8080:8080 parser-api
