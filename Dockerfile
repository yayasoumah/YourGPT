FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download pre-built llamafile with model included
RUN curl -L -o llama2-7b.llamafile https://huggingface.co/jartine/llama-2-7B-chat-llamafile/resolve/main/llama2-7b-chat.Q4_K_M.llamafile && \
    chmod +x llama2-7b.llamafile

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY api_server.py .

EXPOSE 8080

CMD ["python3", "api_server.py"]