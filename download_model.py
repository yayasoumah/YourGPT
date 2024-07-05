import os
from huggingface_hub import hf_hub_download

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    print(f"Downloading {filename} from {model_name}...")
    
    # Use a persistent directory that Railway will maintain across deployments
    model_dir = "/railway/models"
    os.makedirs(model_dir, exist_ok=True)
    
    final_path = os.path.join(model_dir, "llama-2-7b-chat.gguf")
    
    if not os.path.exists(final_path):
        model_path = hf_hub_download(repo_id=model_name, filename=filename)
        os.rename(model_path, final_path)
        print(f"Model downloaded and saved to {final_path}")
    else:
        print(f"Model already exists at {final_path}")
    
    return final_path

if __name__ == "__main__":
    download_model()