#!/bin/bash

# Download the model
python3 download_model.py

# Run the model server
python3 run_model.py &

# Start the API server
gunicorn --bind 0.0.0.0:8080 api_server:app