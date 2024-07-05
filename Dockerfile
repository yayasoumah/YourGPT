FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download Llamafile executable
RUN curl -L -o llamafile https://github.com/Mozilla-Ocho/llamafile/releases/download/0.6/llamafile-0.6 && \
    chmod +x llamafile

# Download the model file
RUN wget -O Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf \
    https://huggingface.co/NumerDox/Llama-3-Instruct-8B-SPPO-Iter3/resolve/main/Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY api_server.py .

EXPOSE 8080

CMD ["python3", "api_server.py"]