# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Download Llamafile executable and model weights
RUN curl -L -o /llamafile https://github.com/Mozilla-Ocho/llamafile/releases/download/0.6/llamafile-0.6 && \
    chmod +x /llamafile && \
    curl -L -o /mistral.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Copy requirements file and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -r /requirements.txt

# Copy the API server
COPY api_server.py /api_server.py

# Expose API port
EXPOSE 8080

# Start the API server using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "api_server:app"]
