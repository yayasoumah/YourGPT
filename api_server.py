import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import subprocess

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/llama-2-7b-chat.gguf')
LLAMA_CPP_PATH = "/llama.cpp"
MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

def start_model_server():
    global MODEL_STATUS, MODEL_PROCESS
    MODEL_STATUS = "STARTING"
    logging.info("Starting Llama-2-7B-Chat model server...")
    
    command = [
        f"{LLAMA_CPP_PATH}/main",
        "-m", MODEL_PATH,
        "--server",
        "--host", "0.0.0.0",
        "--port", "8080"
    ]
    
    MODEL_PROCESS = subprocess.Popen(command, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
    
    while True:
        line = MODEL_PROCESS.stdout.readline()
        logging.info(line.strip())
        if "HTTP server listening" in line:
            MODEL_STATUS = "READY"
            logging.info("Llama-2-7B-Chat model server is ready.")
            break
        elif MODEL_PROCESS.poll() is not None:
            raise Exception("Model server failed to start")

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
        response = subprocess.run([
            "curl", "-X", "POST", "http://localhost:8080/completion",
            "-H", "Content-Type: application/json",
            "-d", f'{{"prompt": "{prompt}", "n_predict": 128}}'
        ], capture_output=True, text=True)
        return jsonify({"response": response.stdout})
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        start_model_server()
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")