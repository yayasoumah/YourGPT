import subprocess
import json
import os
import time
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from download_model import download_model

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

LLAMAFILE_PATH = os.getenv('LLAMAFILE_PATH', './llama2-7b.llamafile')
MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

def log_stage(stage):
    logging.info(f"DEPLOYMENT STAGE: {stage}")

def ensure_model_downloaded():
    log_stage("Ensuring model is downloaded")
    download_model()

def start_model_server():
    global MODEL_STATUS, MODEL_PROCESS
    MODEL_STATUS = "LOADING"
    log_stage(f"Starting Llama-2 model server using {LLAMAFILE_PATH}")
    
    if not os.path.exists(LLAMAFILE_PATH):
        raise FileNotFoundError(f"Llamafile not found at {LLAMAFILE_PATH}")
    
    MODEL_PROCESS = subprocess.Popen([LLAMAFILE_PATH, "--server"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
    
    timeout = 60  # 60 seconds timeout
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Model server startup timed out")
        
        line = MODEL_PROCESS.stdout.readline()
        if "HTTP server listening" in line:
            MODEL_STATUS = "READY"
            log_stage("Llama-2 model server is ready")
            break
        elif MODEL_PROCESS.poll() is not None:
            raise Exception(f"Model server failed to start. Error: {MODEL_PROCESS.stderr.read()}")

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
    if result.returncode != 0:
        raise Exception(f"Failed to get response from model: {result.stderr}")
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
        log_stage(f"Current working directory: {os.getcwd()}")
        log_stage(f"Contents of current directory: {os.listdir('.')}")
        
        ensure_model_downloaded()
        start_model_server()
        
        log_stage("API server starting")
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")
        raise

    