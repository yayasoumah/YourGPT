import os
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO)

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    logging.info(f"Downloading {filename} from {model_name}...")
    
    model_path = hf_hub_download(repo_id=model_name, filename=filename)
    
    os.makedirs("/app/models", exist_ok=True)
    os.rename(model_path, "/app/models/llama-2-7b-chat.gguf")
    
    logging.info(f"Model downloaded and saved to /app/models/llama-2-7b-chat.gguf")

if __name__ == "__main__":
    download_model()