import asyncio
import httpx
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YourGPT", description="Your Personal AI, One Click Away")

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    response: str

async def wait_for_ollama(timeout=120):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama is ready")
                    return
        except httpx.RequestError as e:
            logger.warning(f"Ollama not ready yet: {str(e)}")
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception("Timeout waiting for Ollama to start")
            await asyncio.sleep(1)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def download_model():
    try:
        await wait_for_ollama(timeout=120)
        process = await asyncio.create_subprocess_exec(
            "ollama", "pull", "llama3",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=1800)  # 30 minutes timeout
        if process.returncode != 0:
            logger.error(f"Error downloading model: {stderr.decode()}")
            raise Exception("Failed to download model")
        logger.info("llama3 model downloaded successfully")
    except asyncio.TimeoutError:
        logger.error("Model download timed out")
        raise Exception("Model download timed out")
    except Exception as e:
        logger.error(f"Exception occurred while downloading model: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up YourGPT")
    try:
        await download_model()
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        # You might want to exit the application here if the model download fails
        # import sys
        # sys.exit(1)

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    logger.info(f"Generating response for prompt: {request.prompt}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": request.prompt
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Response generated successfully")
            return GenerateResponse(response=data["response"])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=500, detail="Error generating response from YourGPT")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/")
async def read_root():
    return {"message": "Welcome to YourGPT - Your Personal AI, One Click Away"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)