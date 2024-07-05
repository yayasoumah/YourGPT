#!/bin/bash

# Pull the llama3 model
echo "Pulling llama3 model..."
ollama pull llama3

# Start Ollama server
echo "Starting Ollama server..."
ollama serve

