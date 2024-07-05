import os
import sys
import logging
from llama_cpp import Llama
from llama_cpp.server import app
from download_model import download_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        # Step 1: Download the model
        logging.info("Step 1: Downloading the model")
        model_path = download_model()
        logging.info(f"Model downloaded successfully. Path: {model_path}")

        # Step 2: Verify model file exists
        logging.info("Step 2: Verifying model file")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        logging.info("Model file verified successfully")

        # Step 3: Initialize the Llama model
        logging.info("Step 3: Initializing Llama model")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            chat_format="llama-2"
        )
        logging.info("Llama model initialized successfully")

        # Step 4: Set up the server
        logging.info("Step 4: Setting up the server")
        app.app.state.llm = llm

        # Step 5: Run the server
        logging.info("Step 5: Starting the server")
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)

    except Exception as e:
        logging.error(f"An error occurred during server setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()