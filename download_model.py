import os
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    model_dir = "/app/models"
    
    logging.info(f"Downloading {filename} from {model_name}...")
    
    model_path = hf_hub_download(repo_id=model_name, filename=filename)
    
    os.makedirs(model_dir, exist_ok=True)
    final_path = os.path.join(model_dir, "llama-2-7b-chat.gguf")
    os.rename(model_path, final_path)
    
    logging.info(f"Model downloaded and saved to {final_path}")

if __name__ == "__main__":
    download_model()