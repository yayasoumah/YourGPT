FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Download Llamafile executable
RUN curl -L -o /app/mistral-7b-instruct-v0.2.Q4_0.llamafile https://huggingface.co/jartine/mistral-7b-instruct-v0.2.Q4_0.llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_0.llamafile && \
    chmod +x /app/mistral-7b-instruct-v0.2.Q4_0.llamafile

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY api_server.py /app/api_server.py

EXPOSE 8080

CMD ["python3", "api_server.py"]