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
    local max_attempts=5
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        echo "$(date): Attempt $attempt to pull $model model..."
        if ollama pull $model; then
            echo "$(date): Successfully pulled $model model"
            return 0
        fi
        attempt=$((attempt+1))
        echo "$(date): Failed to pull model. Retrying in 10 seconds..."
        sleep 10
    done
    echo "$(date): Failed to pull model after $max_attempts attempts"
    return 1
}

# Pull the llama3 model
pull_model llama3

# Create a custom model for YourGPT
echo "$(date): Creating custom YourGPT model..."
cat <<EOF > Modelfile
FROM llama2
SYSTEM You are YourGPT, a helpful AI assistant created to provide personalized and private AI interactions.
EOF

ollama create yourgpt -f Modelfile

echo "$(date): Ollama setup complete. Server is ready to handle requests."

# Start the Flask API server
python api_server.py
