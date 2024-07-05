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
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Expose Ollama port
EXPOSE 11434

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting Ollama server..."\n\
ollama serve\n\
' > /start.sh \
&& chmod +x /start.sh

# Run the startup script when the container launches
CMD ["/start.sh"]