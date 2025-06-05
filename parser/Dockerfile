FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl unzip gnupg \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV ENV=DOCKER

COPY parser/requirements.txt ./parser/requirements.txt
RUN pip install --no-cache-dir -r parser/requirements.txt

COPY parser/ ./parser/

EXPOSE 8080

CMD ["uvicorn", "parser.main:app", "--host", "0.0.0.0", "--port", "8080"]