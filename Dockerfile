FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY download_model.py .
COPY api_server.py .

EXPOSE 8080

CMD ["python", "api_server.py"]