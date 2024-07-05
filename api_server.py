import os
import logging
from flask import Flask, request, jsonify
from llama_cpp import Llama
from download_model import download_model, MODEL_PATH

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_STATUS = "NOT_STARTED"
llm = None

def log_stage(stage):
    logging.info(f"DEPLOYMENT STAGE: {stage}")

def load_model():
    global MODEL_STATUS, llm
    MODEL_STATUS = "LOADING"
    log_stage(f"Loading Llama model from {MODEL_PATH}")
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    
    llm = Llama(model_path=MODEL_PATH)
    MODEL_STATUS = "READY"
    log_stage("Llama model is ready")

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
        output = llm(prompt, max_tokens=100)
        return jsonify({"response": output['choices'][0]['text'].strip()})
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        log_stage("Server startup")
        log_stage(f"Current working directory: {os.getcwd()}")
        log_stage(f"Contents of current directory: {os.listdir('.')}")
        
        download_model()
        load_model()
        
        log_stage("API server starting")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    except Exception as e:
        logging.error(f"Failed to start the server: {str(e)}")
        raise


    