# Use Python 3.8 as the base image
FROM python:3.8-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY download_model.py server.py ./

# Create a directory for logs
RUN mkdir /app/logs

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "server.py"]