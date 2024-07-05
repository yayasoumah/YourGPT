import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def download_model():
    model_url = "https://huggingface.co/jartine/llama-2-7B-chat-llamafile/resolve/main/llama2-7b-chat.Q4_K_M.llamafile"
    model_path = "./llama2-7b.llamafile"

    if os.path.exists(model_path):
        logging.info(f"Model already exists at {model_path}")
        return

    logging.info(f"Downloading model from {model_url}")
    result = subprocess.run(["curl", "-L", "-o", model_path, model_url], capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Failed to download model: {result.stderr}")
        raise Exception("Model download failed")

    logging.info(f"Model downloaded successfully to {model_path}")
    
    # Make the model executable
    os.chmod(model_path, 0o755)
    logging.info(f"Made {model_path} executable")

if __name__ == "__main__":
    download_model()