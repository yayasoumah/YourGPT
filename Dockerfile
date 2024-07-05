# Dockerfile
FROM python:3.9

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Start Ollama service and run the FastAPI app
CMD ["sh", "-c", "ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000"]