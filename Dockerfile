# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create a startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for Ollama to start..."\n\
for i in {1..30}; do\n\
    if curl -s http://localhost:11434/api/tags > /dev/null; then\n\
        echo "Ollama is ready"\n\
        break\n\
    fi\n\
    if [ $i -eq 30 ]; then\n\
        echo "Ollama failed to start"\n\
        exit 1\n\
    fi\n\
    sleep 10\n\
done\n\
\n\
# Start the FastAPI application\n\
echo "Starting FastAPI application..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh \
    && chmod +x /app/start.sh

# Run the startup script when the container launches
CMD ["/app/start.sh"]