import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

def download_model():
    model_name = "TheBloke/Llama-2-7B-Chat-GGUF"
    filename = "llama-2-7b-chat.Q4_K_M.gguf"
    
    logging.info(f"Downloading {filename} from {model_name}...")
    
    model_path = hf_hub_download(repo_id=model_name, filename=filename)
    logging.info(f"Model downloaded to {model_path}")
    
    return model_path

def initialize_model():
    model_path = download_model()
    logging.info("Initializing Llama model")
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4,
        chat_format="llama-2"
    )

llm = initialize_model()
logging.info("Llama model initialized successfully")

@app.post("/complete")
async def complete(request: CompletionRequest):
    try:
        response = llm(
            request.prompt,
            max_tokens=request.max_tokens,
            echo=True
        )
        return {"completion": response["choices"][0]["text"]}
    except Exception as e:
        logging.error(f"Error during completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {"message": "YourGPT API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)