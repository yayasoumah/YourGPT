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

# Function to pull the model with retries and timeout
pull_model() {
    local model=$1
    local max_attempts=3
    local timeout=1800  # 30 minutes timeout
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "$(date): Attempt $attempt to pull $model model..."
        
        timeout $timeout ollama pull $model
        pull_exit_code=$?
        
        if [ $pull_exit_code -eq 0 ]; then
            echo "$(date): Successfully pulled $model model"
            return 0
        elif [ $pull_exit_code -eq 124 ]; then
            echo "$(date): Timeout occurred while pulling the model"
        else
            echo "$(date): Failed to pull model (exit code: $pull_exit_code)"
        fi
        
        attempt=$((attempt+1))
        echo "$(date): Retrying in 60 seconds..."
        sleep 60
    done
    
    echo "$(date): Failed to pull model after $max_attempts attempts"
    return 1
}

# Try to pull a smaller model first
if pull_model tinyllama; then
    MODEL="tinyllama"
elif pull_model llama2; then
    MODEL="llama2"
else
    echo "$(date): Failed to pull any model. Exiting."
    exit 1
fi

# Create a custom model for YourGPT
echo "$(date): Creating custom YourGPT model..."
cat <<EOF > Modelfile
FROM $MODEL
SYSTEM You are YourGPT, a helpful AI assistant created to provide personalized and private AI interactions.
EOF

ollama create yourgpt -f Modelfile

echo "$(date): Ollama setup complete. Server is ready to handle requests."

# Start the Flask API server
python3 api_server.py
