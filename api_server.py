import subprocess
import json
import os
import time
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

LLAMAFILE_PATH = os.getenv('LLAMAFILE_PATH', '/app/mistral-7b-instruct-v0.2.Q4_0.llamafile')
MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

def log_stage(stage):
    logging.info(f"DEPLOYMENT STAGE: {stage}")

def download_model():
    log_stage("Downloading Mistral-7B-Instruct model")
    download_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"
    subprocess.run(["wget", "-O", "/app/mistral-7b-instruct-v0.2.Q4_0.gguf", download_url], check=True)
    log_stage("Model download completed")

def start_model_server():
    global MODEL_STATUS, MODEL_PROCESS
    MODEL_STATUS = "LOADING"
    log_stage("Starting Mistral model server")
    MODEL_PROCESS = subprocess.Popen([LLAMAFILE_PATH, "-m", "/app/mistral-7b-instruct-v0.2.Q4_0.gguf", "--server"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
    
    while True:
        line = MODEL_PROCESS.stdout.readline()
        if "HTTP server listening" in line:
            MODEL_STATUS = "READY"
            log_stage("Mistral model server is ready")
            break
        elif MODEL_PROCESS.poll() is not None:
            raise Exception("Model server failed to start")

def run_llamafile(prompt):
    if MODEL_STATUS != "READY":
        raise Exception("Model is not ready yet")
    
    url = "http://localhost:8080/completion"
    data = {
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 100
    }
    command = [
        "curl", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return json.loads(result.stdout)["content"].strip()

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": MODEL_STATUS})

@app.route('/generate', methods=['POST'])
def generate():
    if MODEL_STATUS != "READY":
        return jsonify({"error": "Model is not ready yet"}), 503
    
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        response = run_llamafile(prompt)
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    if MODEL_STATUS != "READY":
        return jsonify({"error": "Model is not ready yet"}), 503
    
    data = request.json
    messages = data.get('messages', [])
    
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    prompt += "\nassistant:"
    
    try:
        response = run_llamafile(prompt)
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        log_stage("Server startup")
        download_model()
        start_model_server()
        log_stage("API server starting")
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")