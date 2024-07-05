import asyncio
import httpx
import logging
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
            await asyncio.sleep(1)

async def warm_up_model():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": "Warm-up request"
                }
            )
        logger.info("Model warmed up successfully")
    except Exception as e:
        logger.error(f"Error warming up model: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    await ensure_ollama_ready()
    await warm_up_model()

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
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