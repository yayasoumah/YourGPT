#!/bin/bash

echo "$(date): Starting Ollama setup..."

# Start Ollama server
echo "$(date): Starting Ollama server..."
ollama serve &

# Wait for Ollama server to start
echo "$(date): Waiting for Ollama server to start..."
until curl -s http://localhost:11434/api/tags >/dev/null; do
    sleep 1
done

echo "$(date): Ollama server is running."

# Function to pull the model with retries
pull_model() {
    local model=$1
    local max_attempts=3
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        echo "$(date): Attempt $attempt to pull $model model..."
        if ollama pull $model; then
            echo "$(date): Successfully pulled $model model"
            return 0
        fi
        attempt=$((attempt+1))
        echo "$(date): Failed to pull model. Retrying in 60 seconds..."
        sleep 60
    done
    echo "$(date): Failed to pull model after $max_attempts attempts"
    return 1
}

# Pull the llama3 model
pull_model llama3

echo "$(date): Ollama setup complete. Server is ready to handle requests."

# Start the Flask API server
python3 api_server.py
