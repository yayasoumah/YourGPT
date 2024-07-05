#!/bin/bash

# Download the model
python3 download_model.py

# Run the model server
python3 run_model.py &

# Wait for the model server to start (you might need to adjust the sleep time)
sleep 10

# Start the API server
python3 api_server.py