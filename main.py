import asyncio
import httpx
import logging
import psutil
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
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
model_ready = asyncio.Event()

def check_memory():
    memory = psutil.virtual_memory()
    logger.info(f"Available memory: {memory.available / (1024 * 1024 * 1024):.2f} GB")
    if memory.available < 1 * 1024 * 1024 * 1024:  # Less than 1GB available
        logger.warning("Low memory condition detected")

async def ensure_ollama_ready():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama is ready")
                    return
        except httpx.RequestError as e:
            logger.warning(f"Ollama not ready yet: {str(e)}")
        await asyncio.sleep(5)  # Wait for 5 seconds before retrying

async def load_model():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": "Warm-up request"
                }
            )
        logger.info("Model loaded successfully")
        model_ready.set()  # Signal that the model is ready
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        # Don't raise here, let the application continue running

async def startup_sequence():
    check_memory()
    await ensure_ollama_ready()
    await load_model()

@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(startup_sequence)
    # Don't await here, let it run in the background

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    check_memory()
    if not model_ready.is_set():
        raise HTTPException(status_code=503, detail="Model is not ready yet. Please try again later.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": request.prompt
                }
            )
            response.raise_for_status()
            data = response.json()
            return GenerateResponse(response=data["response"])
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error generating response from YourGPT")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/health")
async def health_check():
    check_memory()
    if not model_ready.is_set():
        return {"status": "starting", "message": "Model is still loading"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return {"status": "healthy"}
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