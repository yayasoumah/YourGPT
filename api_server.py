import subprocess
import json
import os
import time
from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

LLAMAFILE_PATH = os.getenv('LLAMAFILE_PATH', '/llamafile')
MODEL_PATH = os.getenv('MODEL_PATH', '/mistral.gguf')
MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

def start_model_server():
    global MODEL_STATUS, MODEL_PROCESS
    MODEL_STATUS = "LOADING"
    logging.info("Starting Mistral model server...")
    MODEL_PROCESS = subprocess.Popen([LLAMAFILE_PATH, "-m", MODEL_PATH, "--server"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
    
    # Wait for the server to start
    while True:
        line = MODEL_PROCESS.stdout.readline()
        if "HTTP server listening" in line:
            MODEL_STATUS = "READY"
            logging.info("Mistral model server is ready.")
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
    
    # Construct a prompt from the messages
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
        start_model_server()
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")
