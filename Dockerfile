# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /requirements.txt

# Download Mistral Llamafile
RUN curl -L -o /mistral-7b-instruct-v0.2.Q4_0.llamafile https://huggingface.co/jartine/mistral-7b-instruct-v0.2.Q4_0.llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_0.llamafile && \
    chmod +x /mistral-7b-instruct-v0.2.Q4_0.llamafile

# Copy the API server
COPY api_server.py /api_server.py

# Expose API port
EXPOSE 8080

# Start the API server
CMD ["python3", "api_server.py"]
