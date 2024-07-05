# main.py
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="YourGPT", description="Your Personal AI, One Click Away")

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    response: str

async def download_model():
    try:
        process = await asyncio.create_subprocess_exec(
            "ollama", "pull", "gemma2:9b",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"Error downloading model: {stderr.decode()}")
            raise Exception("Failed to download model")
        print("Gemma 2 9B model downloaded successfully")
    except Exception as e:
        print(f"Exception occurred while downloading model: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    await download_model()

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma2:9b",
                "prompt": request.prompt
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error generating response from YourGPT")
        data = response.json()
        return GenerateResponse(response=data["response"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to YourGPT - Your Personal AI, One Click Away"}
