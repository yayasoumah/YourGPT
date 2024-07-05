import os
import logging
from llama_cpp import Llama
from llama_cpp.server import app
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    logging.info(f"Downloading {filename} from {model_name}...")
    
    model_path = hf_hub_download(repo_id=model_name, filename=filename)
    logging.info(f"Model downloaded to {model_path}")
    
    return model_path

def main():
    try:
        # Step 1: Download the model
        logging.info("Step 1: Downloading the model")
        model_path = download_model()

        # Step 2: Initialize the Llama model
        logging.info("Step 2: Initializing Llama model")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            chat_format="llama-2"
        )
        logging.info("Llama model initialized successfully")

        # Step 3: Set up the server
        logging.info("Step 3: Setting up the server")
        app.app.state.llm = llm

        # Step 4: Run the server
        logging.info("Step 4: Starting the server")
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)

    except Exception as e:
        logging.error(f"An error occurred during server setup: {str(e)}")
        raise

if __name__ == "__main__":
    main()