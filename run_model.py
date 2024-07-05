import subprocess
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_model():
    model_path = "/app/models/llama-2-7b-chat.gguf"
    if not os.path.exists(model_path):
        logging.error(f"Model file not found at {model_path}")
        sys.exit(1)

    command = [
        "llama",
        "-m", model_path,
        "--server",
        "--host", "0.0.0.0",
        "--port", "8080"
    ]

    logging.info("Starting Llama-2-7B-Chat model server...")

    try:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        for line in process.stdout:
            logging.info(line.strip())
            if "HTTP server listening" in line:
                logging.info("Llama-2-7B-Chat model server is ready.")
                break

        # Check if the process has terminated
        if process.poll() is not None:
            logging.error(f"Process terminated with return code {process.returncode}")
            for line in process.stderr:
                logging.error(line.strip())
            sys.exit(1)

        return process
    except Exception as e:
        logging.error(f"Error starting the model server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_model()