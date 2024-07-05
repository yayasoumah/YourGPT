#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

echo "$(date): Starting Ollama setup..."

# Start Ollama server and capture its output
echo "$(date): Starting Ollama server..."
ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama server to start and capture the port
echo "$(date): Waiting for Ollama server to start..."
OLLAMA_PORT=""
TIMEOUT=60
START_TIME=$(date +%s)

while [ -z "$OLLAMA_PORT" ]; do
    if ! kill -0 $OLLAMA_PID 2>/dev/null; then
        echo "$(date): Error: Ollama server process has died."
        cat ollama.log
        exit 1
    fi

    CURRENT_TIME=$(date +%s)
    if [ $((CURRENT_TIME - START_TIME)) -ge $TIMEOUT ]; then
        echo "$(date): Timeout waiting for Ollama server to start. Using default port 11434."
        OLLAMA_PORT=11434
        break
    fi

    OLLAMA_PORT=$(grep -oP 'port="\K[0-9]+' ollama.log | tail -1)
    if [ -z "$OLLAMA_PORT" ]; then
        echo "$(date): Waiting for port information..."
        sleep 5
    fi
done

echo "$(date): Ollama server is running on port $OLLAMA_PORT."

# Export the OLLAMA_PORT for the Python script to use
export OLLAMA_PORT

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

# Print the contents of ollama.log for debugging
echo "$(date): Contents of ollama.log:"
cat ollama.log

# Start the Flask API server
python3 api_server.py
