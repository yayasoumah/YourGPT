#!/bin/bash

# Function to pull the model with retries
pull_model() {
    local max_attempts=5
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        echo "$(date): Attempt $attempt to pull llama3 model..."
        if ollama pull llama3; then
            echo "$(date): Successfully pulled llama3 model"
            return 0
        fi
        attempt=$((attempt+1))
        echo "$(date): Failed to pull model. Retrying in 10 seconds..."
        sleep 10
    done
    echo "$(date): Failed to pull model after $max_attempts attempts"
    return 1
}

echo "$(date): Starting Ollama setup..."

# Pull the llama3 model
pull_model

# Start Ollama server
echo "$(date): Starting Ollama server..."
ollama serve