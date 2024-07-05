import os
import requests

MODEL_URL = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin"
MODEL_PATH = "./llama-2-7b-chat.ggmlv3.q4_0.bin"

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
        return MODEL_PATH

    print(f"Downloading model from {MODEL_URL}")
    response = requests.get(MODEL_URL, stream=True)
    response.raise_for_status()

    with open(MODEL_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Model downloaded successfully to {MODEL_PATH}")
    return MODEL_PATH

if __name__ == "__main__":
    download_model()