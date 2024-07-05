# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone and build llama.cpp
RUN git clone https://github.com/ggerganov/llama.cpp.git && \
    cd llama.cpp && \
    make && \
    cp main /usr/local/bin/llama

# Copy requirements file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the application files
COPY api_server.py download_model.py run_model.py start.sh /app/

# Set the working directory
WORKDIR /app

# Make the start script executable
RUN chmod +x start.sh

# Expose API port
EXPOSE 8080

# Start the application
CMD ["./start.sh"]