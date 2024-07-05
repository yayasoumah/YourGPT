import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def run_model():
    model_path = "/app/models/llama-2-7b-chat.gguf"
    command = [
        "/llama.cpp/main",
        "-m", model_path,
        "--server",
        "--host", "0.0.0.0",
        "--port", "8080"
    ]
    
    logging.info("Starting Llama-2-7B-Chat model server...")
    
    process = subprocess.Popen(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               universal_newlines=True)
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        logging.info(line.strip())
        if "HTTP server listening" in line:
            logging.info("Llama-2-7B-Chat model server is ready.")
            break
    
    return process

if __name__ == "__main__":
    run_model()

    