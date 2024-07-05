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
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create directory for supervisor configs
RUN mkdir -p /etc/supervisor/conf.d

# Copy supervisor configuration file
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Copy the startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose Ollama port
EXPOSE 11434

# Start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]