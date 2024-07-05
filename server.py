import os
from llama_cpp import Llama
from llama_cpp.server import app
from download_model import download_model

def main():
    # Download the model if it doesn't exist
    model_path = "/app/models/llama-2-7b-chat.gguf"
    if not os.path.exists(model_path):
        model_path = download_model()

    # Initialize the Llama model
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,  # Increase context window
        n_threads=4,  # Adjust based on your CPU
        chat_format="llama-2"  # Use the Llama-2 chat format
    )

    # Set the global llm instance for the server
    app.app.state.llm = llm

    # Run the server
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

    