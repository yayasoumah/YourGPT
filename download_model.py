import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def download_file(url, filename):
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        logging.info(f"{filename} already exists at {filepath}")
        return filepath

    logging.info(f"Downloading {filename} from {url}")
    result = subprocess.run(["curl", "-L", "-o", filepath, url], capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Failed to download {filename}: {result.stderr}")
        raise Exception(f"{filename} download failed")

    logging.info(f"{filename} downloaded successfully to {filepath}")
    
    # Make the file executable
    os.chmod(filepath, 0o755)
    logging.info(f"Made {filepath} executable")
    
    return filepath

def download_llamafile_and_model():
    llamafile_url = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.1/llamafile-0.1"
    llamafile_path = download_file(llamafile_url, "llamafile")
    
    model_url = "https://huggingface.co/jartine/llama-2-7B-chat-llamafile/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
    model_path = download_file(model_url, "llama-2-7b-chat.Q4_K_M.gguf")
    
    return llamafile_path, model_path

if __name__ == "__main__":
    download_llamafile_and_model()