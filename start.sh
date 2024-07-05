#!/bin/bash

# Set environment variables
export $(cat .env | xargs)

# Download the model
python3 download_model.py

# Run the model server
python3 run_model.py &

# Start the API server
gunicorn --bind 0.0.0.0:$PORT api_server:app