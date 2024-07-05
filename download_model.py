import os
from huggingface_hub import hf_hub_download

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    print(f"Downloading {filename} from {model_name}...")
    
    model_path = hf_hub_download(repo_id=model_name, filename=filename)
    
    os.makedirs("/app/models", exist_ok=True)
    final_path = "/app/models/llama-2-7b-chat.gguf"
    os.rename(model_path, final_path)
    
    print(f"Model downloaded and saved to {final_path}")
    return final_path

if __name__ == "__main__":
    download_model()