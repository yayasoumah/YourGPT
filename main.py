import asyncio
import httpx
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YourGPT", description="Your Personal AI, One Click Away")

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    response: str

# Global variable to track if the model is ready
model_ready = False

# Use environment variable for Ollama URL, default to localhost if not set
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

async def ensure_ollama_ready():
    max_retries = 30
    for i in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OLLAMA_URL}/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama is ready")
                    return
        except httpx.RequestError as e:
            logger.warning(f"Ollama not ready yet (attempt {i+1}/{max_retries}): {str(e)}")
        await asyncio.sleep(10)  # Wait for 10 seconds before retrying
    logger.error("Ollama failed to start after maximum retries")
    raise Exception("Ollama failed to start")

async def load_model():
    global model_ready
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": "Warm-up request"
                },
                timeout=600.0  # 10 minutes timeout
            )
        logger.info("Model loaded successfully")
        model_ready = True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up YourGPT")
    try:
        await ensure_ollama_ready()
        await load_model()
        logger.info("YourGPT startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        # We'll let the application start, but it won't be able to generate responses

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model is not ready yet. Please try again later.")
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Sending request to Ollama with prompt: {request.prompt[:50]}...")
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": request.prompt
                },
                timeout=120.0  # 2 minutes timeout for generation
            )
            logger.info(f"Received response from Ollama with status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully generated response")
            return GenerateResponse(response=data["response"])
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        if e.response.status_code == 404:
            raise HTTPException(status_code=500, detail="Ollama API endpoint not found. Please check if Ollama is running correctly.")
        else:
            raise HTTPException(status_code=500, detail=f"Error generating response from YourGPT: {str(e)}")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200 and model_ready:
                return {"status": "healthy", "message": "Ollama is responding and model is loaded"}
            elif response.status_code == 200:
                return {"status": "partially healthy", "message": "Ollama is responding but model is not yet loaded"}
            else:
                return {"status": "unhealthy", "message": "Ollama is not responding correctly"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "message": str(e)}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)