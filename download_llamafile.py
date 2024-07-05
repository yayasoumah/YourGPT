import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

LLAMAFILE_URL = "https://huggingface.co/jartine/llava-v1.5-7B-llamafile/resolve/main/llava-v1.5-7b-q4.llamafile"
LLAMAFILE_PATH = "./llava-v1.5-7b-q4.llamafile"

def download_llamafile():
    if os.path.exists(LLAMAFILE_PATH):
        logging.info(f"Llamafile already exists at {LLAMAFILE_PATH}")
        return LLAMAFILE_PATH

    logging.info(f"Downloading Llamafile from {LLAMAFILE_URL}")
    result = subprocess.run(["curl", "-L", "-o", LLAMAFILE_PATH, LLAMAFILE_URL], capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Failed to download Llamafile: {result.stderr}")
        raise Exception("Llamafile download failed")

    logging.info(f"Llamafile downloaded successfully to {LLAMAFILE_PATH}")
    
    # Make the file executable
    os.chmod(LLAMAFILE_PATH, 0o755)
    logging.info(f"Made {LLAMAFILE_PATH} executable")
    
    return LLAMAFILE_PATH

if __name__ == "__main__":
    download_llamafile()