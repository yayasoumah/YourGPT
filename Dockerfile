# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV OLLAMA_HOST 0.0.0.0
ENV OLLAMA_MODELS /root/.ollama/models

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements file
COPY requirements.txt /requirements.txt

# Upgrade pip and install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r /requirements.txt

# Copy the startup script and API server
COPY start.sh /start.sh
COPY api_server.py /api_server.py
RUN chmod +x /start.sh

# Expose Ollama port and API port
EXPOSE 11434 8080

# Start the Ollama server and API server
CMD ["/start.sh"]
