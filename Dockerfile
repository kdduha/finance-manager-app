FROM python:3.11-slim

# install make
RUN apt-get update && apt-get install -y make && apt-get clean

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["make", "run-local"]
