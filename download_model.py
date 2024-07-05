import os
import sys
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    logging.info(f"Attempting to download {filename} from {model_name}...")
    
    # Use the current directory as the model directory
    model_dir = os.path.dirname(os.path.abspath(__file__))
    final_path = os.path.join(model_dir, "llama-2-7b-chat.gguf")
    
    try:
        if not os.path.exists(final_path):
            logging.info(f"Model not found. Downloading to {final_path}")
            model_path = hf_hub_download(repo_id=model_name, filename=filename)
            os.rename(model_path, final_path)
            logging.info(f"Model downloaded and saved to {final_path}")
        else:
            logging.info(f"Model already exists at {final_path}")
        
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"Model file not found at {final_path} after download attempt")
        
        return final_path
    except Exception as e:
        logging.error(f"An error occurred while downloading the model: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        model_path = download_model()
        print(f"Model path: {model_path}")
    except Exception as e:
        logging.error(f"Failed to download model: {str(e)}")
        sys.exit(1)