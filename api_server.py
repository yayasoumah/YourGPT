import subprocess
import os
import time
import logging
from flask import Flask, request, jsonify
from download_llamafile import download_llamafile, LLAMAFILE_PATH

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

def log_stage(stage):
    logging.info(f"DEPLOYMENT STAGE: {stage}")

def start_model_server():
    global MODEL_STATUS, MODEL_PROCESS
    MODEL_STATUS = "LOADING"
    log_stage(f"Starting Llava model server using {LLAMAFILE_PATH}")
    
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
            log_stage("Llava model server is ready")
            break
        elif MODEL_PROCESS.poll() is not None:
            raise Exception(f"Model server failed to start. Error: {MODEL_PROCESS.stderr.read()}")

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
        url = "http://localhost:8080/completion"
        command = [
            "curl", "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", f'{{"prompt": "{prompt}", "temperature": 0.7, "max_tokens": 100}}'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to get response from model: {result.stderr}")
        response = result.stdout.strip()
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        log_stage("Server startup")
        log_stage(f"Current working directory: {os.getcwd()}")
        log_stage(f"Contents of current directory: {os.listdir('.')}")
        
        download_llamafile()
        start_model_server()
        
        log_stage("API server starting")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")
        raise